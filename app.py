import streamlit as st
import fitz  # PyMuPDF
import os
import cv2
import numpy as np
from utills.detect_bbox import extract_bbox_with_text
from utills.utills import Image
from utills.utills import utills

def init_session_state():
    """
    Initialize all required session state variables if not already set.
    """
    if "pdf_file" not in st.session_state:
        st.session_state.pdf_file = None
    if "pdf_doc" not in st.session_state:
        st.session_state.pdf_doc = None
    if "uploaded_images" not in st.session_state:
        # { page_num: PIL.Image }
        st.session_state.uploaded_images = {}
        st.session_state.corrected_upload_images = {}
        st.session_state.page_num_idx = 0
    if "extraction_results" not in st.session_state:
        # extraction_results[page_number] = [
        #   { "bbox": (...), "text": "...", "approved": bool, "pl": int, "pr": int, "pt": int, "pb": int }
        # ]
        st.session_state.extraction_results = {}
    if "current_page_num" not in st.session_state:
        # Which PDF page the user is on
        st.session_state.current_page_num = 0
    # if "segment_page_num" not in st.session_state:
    #     # Pagination index among text segments
    #     st.session_state.segment_page_num = 0


def render_dpad(line_info, key_prefix="arrow"):
    # Initialize padding history if not already done
    if "padding_history" not in line_info:
        line_info["padding_history"] = [(0, 0, 0, 0)]

    # Use session state to track toggle state
    if f"{key_prefix}_edit_mode" not in st.session_state:
        st.session_state[f"{key_prefix}_edit_mode"] = False

    # If edit mode is not active, show the "Edit" button
    if not st.session_state[f"{key_prefix}_edit_mode"]:
        if st.button("Adjust", key=f"{key_prefix}_edit_button"):
            st.session_state[f"{key_prefix}_edit_mode"] = True
            st.rerun(scope="fragment")
    else:
        # Render the D-pad
        row1 = st.columns([1, 1, 1])
        with row1[0]:
            if st.button("↺", key=f"{key_prefix}_reset"):
                line_info["pb"] = 0
                line_info["pt"] = 0
                line_info["pl"] = 0
                line_info["pr"] = 0
                line_info["padding_history"] = [(0, 0, 0, 0)]
                line_info["padding_corrected"] = False
                st.rerun(scope="fragment")
        with row1[1]:
            if st.button("▲", key=f"{key_prefix}_expand_up"):
                line_info["pb"] += 5
                line_info["padding_history"].append((line_info["pl"], line_info["pr"], line_info["pt"], line_info["pb"]))
                line_info["padding_corrected"] = True
                st.rerun(scope="fragment")
        with row1[2]:
            undo_disabled = len(line_info["padding_history"]) <= 1
            if st.button("↶", key=f"{key_prefix}_undo", disabled=undo_disabled):
                if len(line_info["padding_history"]) > 1:
                    line_info["padding_history"].pop()
                    pl, pr, pt, pb = line_info["padding_history"][-1]
                    line_info["pl"] = pl
                    line_info["pr"] = pr
                    line_info["pt"] = pt
                    line_info["pb"] = pb
                    if len(line_info["padding_history"]) == 1:
                        line_info["padding_corrected"] = False
                    st.rerun(scope="fragment")

        row2 = st.columns([1, 1, 1])
        with row2[0]:
            if st.button("◀", key=f"{key_prefix}_expand_left"):
                line_info["pl"] += 10
                line_info["padding_history"].append((line_info["pl"], line_info["pr"], line_info["pt"], line_info["pb"]))
                line_info["padding_corrected"] = True
                st.rerun(scope="fragment")
        with row2[1]:
             if st.button("▼", key=f"{key_prefix}_expand_down"):
                line_info["pt"] += 5
                line_info["padding_history"].append((line_info["pl"], line_info["pr"], line_info["pt"], line_info["pb"]))
                line_info["padding_corrected"] = True
                st.rerun(scope="fragment")
        with row2[2]:
            if st.button("▶", key=f"{key_prefix}_expand_right"):
                line_info["pr"] += 10
                line_info["padding_history"].append((line_info["pl"], line_info["pr"], line_info["pt"], line_info["pb"]))
                line_info["padding_corrected"] = True
                st.rerun(scope="fragment")

        row3 = st.columns([1, 1, 1])
        with row3[1]:
            if st.button("▽", key=f"{key_prefix}_shrink_up"):
                line_info["pb"] -= 2
                line_info["padding_history"].append((line_info["pl"], line_info["pr"], line_info["pt"], line_info["pb"]))
                line_info["padding_corrected"] = True
                st.rerun(scope="fragment")

        row4 = st.columns([1, 1, 1])
        with row4[0]:
            if st.button("▷", key=f"{key_prefix}_shrink_left"):
                line_info["pl"] -= 20
                line_info["padding_history"].append((line_info["pl"], line_info["pr"], line_info["pt"], line_info["pb"]))
                line_info["padding_corrected"] = True
                st.rerun(scope="fragment")
        with row4[1]:
             if st.button("△", key=f"{key_prefix}_shrink_down"):
                line_info["pt"] -= 2
                line_info["padding_history"].append((line_info["pl"], line_info["pr"], line_info["pt"], line_info["pb"]))
                line_info["padding_corrected"] = True
                st.rerun(scope="fragment")
        with row4[2]:
            if st.button("◁", key=f"{key_prefix}_shrink_right"):
                line_info["pr"] -= 20
                line_info["padding_history"].append((line_info["pl"], line_info["pr"], line_info["pt"], line_info["pb"]))
                line_info["padding_corrected"] = True
                st.rerun(scope="fragment")




@st.fragment
def show_segment_compact(segment_idx, line_info, base_img, unique_tag=""):
    """
    Renders a single segment in a compact layout:
      (1) Editable text area above
      (2) Single row: cropped image | D-pad | approve/ignore
    """
    col_text, col_dpad_title, col_approve_title = st.columns([0.8, 0.1, 0.1])
    with col_text:

        text_key = f"text_{unique_tag}_{segment_idx}"

        if "original_text" not in line_info:
            line_info["original_text"] = line_info["text"]

        new_text = st.text_input(
            f"Edit text (Segment #{segment_idx+1}):",
            value=line_info["text"],
            key=text_key,
            label_visibility="collapsed"
        )

        # Compare to original
        if new_text != line_info["original_text"]:
            line_info["text_corrected"] = True
            line_info["text"] = new_text
    with col_dpad_title:
        st.markdown("**Padding**")

    with col_approve_title:
        st.markdown("**Status**")

    col_img, col_dpad, col_approve = st.columns([0.8, 0.1, 0.1])

    # (A) Cropped image
    with col_img:
        cropped_img = Image(base_img).crop(
            line_info["bbox"],
            pl=line_info["pl"],
            pr=line_info["pr"],
            pt=line_info["pt"],
            pb=line_info["pb"]
        )
        st.image(cropped_img )

    # (B) D-pad
    with col_dpad:
        render_dpad(line_info, key_prefix=f"{unique_tag}_{segment_idx}")

    # (C) Approve / Ignore
    with col_approve:
        # Approve Button
        approve_key = f"approve_{unique_tag}_{segment_idx}"

        # Initialize session state for the approval toggle if not already done
        toggle_key = f"{approve_key}_toggle"
        if toggle_key not in st.session_state:
            st.session_state[toggle_key] = line_info["approved"]

        # Determine button label and color based on session state
        button_label = "✅ Approved" if st.session_state[toggle_key] else "❌ Rejected"

        # Render the button
        if st.button(button_label, key=approve_key):
            # Toggle the approval state in session state
            st.session_state[toggle_key] = not st.session_state[toggle_key]
            line_info["approved"] = st.session_state[toggle_key]
            st.rerun(scope="fragment")
@st.fragment
def download_btn(all_segments,page_num):
    if st.button("Generate ZIP"):
        zip_data = utills.create_result_zip(st.session_state.corrected_upload_images[page_num], all_segments, page_num)  
        st.download_button(
                        label="Download ZIP",
                        data=zip_data,
                        file_name=f"{st.session_state.pdf_file.name}_page_{page_num}_results.zip",
                        mime="application/zip")
        # st.rerun(scope="fragment")

# --------------------------------------------------------------------
# 5) Main Streamlit App
# --------------------------------------------------------------------
def main():
    st.set_page_config(
        page_title="OCR Dataset Creator", 
        page_icon="🔡",  
        layout="wide")
    init_session_state()

    

    st.title("OCR Dataset Auto Annotator")
    # Two tabs
    tab_upload, tab_approve, tab_how = st.tabs(["Upload Files", "Annotation","How to Use"])

    # ---- TAB 1: UPLOAD & PROGRESS
    with tab_upload:
        st.header("1. Upload PDF")
        pdf_file = st.file_uploader("Select a PDF file", type=["pdf"], key="pdf_uploader")
        if pdf_file is not None:
            # Load PDF
            st.session_state.pdf_doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
            st.session_state.pdf_file = pdf_file
        else:
            # Clear PDF when removed
            st.session_state.pdf_file = None
            st.session_state.pdf_doc = None
            st.session_state.extraction_results = {}
            st.session_state.corrected_upload_images = {}
            st.session_state.page_num_idx = 0

        st.header("2. Upload Page Images")
        st.write("Name each file as `page_{page_num}.jpg` or `.png` to match the PDF page.")
        uploaded_imgs = st.file_uploader("Upload page images", 
                                         type=["jpg","jpeg","png"],
                                         accept_multiple_files=True)
        
        # Track uploaded file names to detect changes
        current_file_names = set([f.name for f in uploaded_imgs]) if uploaded_imgs else set()
        if "last_uploaded_file_names" not in st.session_state:
            st.session_state.last_uploaded_file_names = set()
        
        # Only clear if files actually changed
        if current_file_names != st.session_state.last_uploaded_file_names:
            st.session_state.uploaded_images = {}
            st.session_state.corrected_upload_images = {}
            st.session_state.extraction_results = {}
            st.session_state.page_num_idx = 0
            st.session_state.last_uploaded_file_names = current_file_names
        
        if uploaded_imgs:
            for img_file in uploaded_imgs:
                fname = img_file.name
                try:
                    pnum_str = fname.split("_")[1].split(".")[0]
                    pnum = int(pnum_str)
                    
                    # Only process if not already in uploaded_images
                    if pnum not in st.session_state.uploaded_images:
                        # Read the uploaded file as a byte array
                        file_bytes = np.asarray(bytearray(img_file.read()), dtype=np.uint8)

                        # Decode the byte stream to an image (OpenCV reads it in BGR format)
                        image_bgr = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

                        # Convert the image to RGB format
                        image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)

                        st.session_state.uploaded_images[pnum] = image_rgb
                except Exception as e:
                    st.warning(f"Could not parse page number from filename: {fname}")
        else:
            # Clear session state when no files are uploaded
            if st.session_state.uploaded_images:  # Only if there were files before
                st.session_state.uploaded_images = {}
                st.session_state.corrected_upload_images = {}
                st.session_state.extraction_results = {}
                st.session_state.page_num_idx = 0
                st.session_state.last_uploaded_file_names = set()

        # Show status
        pdf_pages_count = len(st.session_state.pdf_doc) if st.session_state.pdf_doc else 0
        uploaded_images = st.session_state.uploaded_images
        st.write(f"**PDF Pages Count**: {pdf_pages_count}")
        st.write(f"**Uploaded Images Count**: {len(uploaded_images)}")

    # ---- TAB 2: APPROVAL & REJECTION
    with tab_approve:
        st.header("Auto Annotations")

        if not st.session_state.pdf_doc or len(st.session_state.uploaded_images) == 0:
            st.warning("Please upload a PDF and its corresponding page images first.")
        else:
            num_pdf_pages = pdf_pages_count
            # Sort uploaded image page numbers for consistent navigation
            sorted_img_pages = sorted(list(uploaded_images.keys()))
            # Clamp navigation index to available images
            st.session_state.page_num_idx = max(0, min(st.session_state.page_num_idx, len(sorted_img_pages)-1))
            page_num = sorted_img_pages[st.session_state.page_num_idx]
            # Guard: uploaded image page may exceed PDF page count
            if page_num >= num_pdf_pages:
                st.warning(f"Uploaded image references page {page_num+1}, but PDF has only {num_pdf_pages} pages.")
                st.markdown(f"**Viewing Image Page: {page_num+1} / {len(sorted_img_pages)}**")
            else:
                st.markdown(f"**Viewing Page: {page_num+1} / {num_pdf_pages}**")
            # st.markdown(f"**Image: {page_num+1} / {len(list(uploaded_images.keys()))}**")
            current_img = st.session_state.uploaded_images.get(page_num)
            if current_img is None:
                st.warning(f"No scanned image found for page {page_num}.")
            else:
                # Extract bounding boxes if not done
                if page_num not in st.session_state.extraction_results and page_num < num_pdf_pages:
                    try:
                        pdf_page = st.session_state.pdf_doc.load_page(page_num)
                    except Exception as e:
                        st.error(f"Failed to load PDF page {page_num}: {e}")
                        st.stop()
                    try:
                        extracted, corrected_current_img = extract_bbox_with_text(pdf_page, current_img)
                    except Exception as e:
                        st.error(f"Extraction error on page {page_num}: {e}")
                        st.stop()
                    
                    st.session_state.corrected_upload_images[page_num] = corrected_current_img
                    st.session_state.extraction_results[page_num] = []
                    for bbox,text in extracted.items():
                        if len(text)<=5:
                            continue
                        st.session_state.extraction_results[page_num].append({
                            "bbox": bbox,
                            "text": text,
                            "approved": True,
                            "text_corrected": False,
                            "padding_corrected": False,
                            "pl": 0, "pr": 0, "pt": 0, "pb": 0,
                            "padding_history": [(0, 0, 0, 0)]
                        })
                    

                all_segments = st.session_state.extraction_results[page_num]
                
                # total_segments = len(all_segments)

                # st.write("Segments per page:")
                # items_per_page = st.number_input(" ", min_value=1, max_value=50, value=20)
                # start_idx = st.session_state.segment_page_num * items_per_page
                # end_idx   = start_idx + items_per_page
                # segment_slice = all_segments[start_idx:end_idx]

                # seg_nav_left, seg_nav_mid, seg_nav_right = st.columns([1,2,1])
                # with seg_nav_left:
                #     if st.button("Prev Segments", disabled=(start_idx<=0)):
                #         st.session_state.segment_page_num -= 1
                #         st.stop()
                # with seg_nav_mid:
                #     if total_segments > 0:
                #         total_seg_pages = (total_segments-1)//items_per_page + 1
                #         st.write(f"Segment Page {st.session_state.segment_page_num+1}/{total_seg_pages}")
                # with seg_nav_right:
                #     if st.button("Next Segments", disabled=(end_idx>=total_segments)):
                #         st.session_state.segment_page_num += 1
                #         st.stop()

                # Show each segment
                for global_idx, seg_info in enumerate(all_segments):
                    text = f"Segment #{global_idx+1}"
                    st.markdown(f"""
                        <div style="display: flex; align-items: center;">
                            <span style="margin-right: 10px; margin-top: 2px; margin-bottom: 0px  padding-bottom: 0px; font-weight: bold;">{text}</span>
                            <hr style="flex-grow: 1; border: 1px solid #ccc;">
                        </div>
                        """, unsafe_allow_html=True)
                    show_segment_compact(global_idx, seg_info, st.session_state.corrected_upload_images[page_num], unique_tag=str(page_num))

                st.divider()
                # Page nav
                nav_left,dummuy_col_1,dummuy_col_2 ,nav_mid,dummuy_col_3,dummuy_col_4, nav_right = st.columns(7)
                with nav_left:
                    st.markdown("<div style='text-align: right;'>", unsafe_allow_html=True)
                    if st.button("⬅️ Prev Page", disabled=(st.session_state.page_num_idx<=0)):
                        st.session_state.page_num_idx -= 1
                        # Reset segment pagination
                        # st.session_state.segment_page_num = 0
                        st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)
                with nav_mid:
                    st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
                    if page_num < num_pdf_pages:
                        st.markdown(f"**Viewing Page: {page_num+1} / {num_pdf_pages}**")
                    else:
                        st.markdown(f"**Viewing Image Page: {page_num+1} / {len(sorted_img_pages)}**")
                    st.markdown("</div>", unsafe_allow_html=True)
                    download_btn(all_segments,page_num)
                with nav_right:                    
                    if st.button("Next Page ➡️", disabled=(st.session_state.page_num_idx>=len(sorted_img_pages)-1)):
                        st.session_state.page_num_idx += 1
                        # st.session_state.segment_page_num = 0
                        st.rerun()
    with tab_how:
        st.header("How to Use the OCR Dataset Auto Annotator")
        # Sample File Download Section
        

        st.markdown("### Sample Images")
        sample_images = [
            {"path": "sample_files/page_0.jpg", "label": "Test Img 0"},
            {"path": "sample_files/page_1.jpg", "label": "Test Img 1"},
            {"path": "sample_files/page_2.jpg", "label": "Test Img 2"},
            {"path": "sample_files/page_3.jpg", "label": "Test Img 3"},
            {"path": "sample_files/page_4.jpg", "label": "Test Img 4"},
        ]

        # Create download buttons inline using columns
        
        st.markdown("""
        
        ### 1. Upload Files
        - Navigate to the **Upload Files** tab.
        - Upload your **PDF file**:
            - Click on "Select a PDF file" and upload the desired PDF.""")
        st.markdown("- Use following Sample PDF file for testing")
        with open("sample_files/sample.pdf", "rb") as pdf_file:
            pdf_data = pdf_file.read()
        st.download_button(
            label="Download Sample PDF",
            data=pdf_data,
            file_name="sample.pdf",
            mime="application/pdf",
        )
        st.markdown("""
        - Upload **corresponding page images**:
            - Images should be named in the format `page_{page_num}.jpg` or `.png`.
            - Ensure the page numbers in the image names match the pages in the PDF.
        - Use following sample images for testing
        """)
        cols = st.columns(12)
        for col, image in zip(cols, sample_images):
            with col:
                with open(image["path"], "rb") as img_file:
                    img_data = img_file.read()
                st.download_button(
                    label=image["label"],
                    data=img_data,
                    file_name=image["path"].split("/")[-1],
                    mime="image/jpeg",
                )
        st.markdown("""
        ### 2. Auto Annotation
        - Navigate to the **Annotation** tab.
        - You will see auto annotated results (page wise).
        - For each page:
            - View the extracted text segments with their cropped image.
            - Use the **Adjust** button for padding adjustments:
                - Use directional buttons (**▲, ▼, ◀, ▶**) to modify padding.
                - Use the **↺ Reset** button to reset padding adjustments.
            - Correct text annotation if wrong
               
            - Reject unwanted annotation pairs:
                - Click the status button (**✅ Approved** or **❌ Rejected**) to change the approval status.

        ### 3. Download Results
        - After reviewing and adjusting the annotations:
            - Click the **Generate ZIP** button to create a ZIP file with results.
            - The ZIP file contains:
                - Cropped images for each segment.
                - A CSV file with image name and annotated text.
            - Click **Download ZIP** to save the file(one zip file per page).
        #### Go to Next page and repeat process
        

        ### Notes:
        - Ensure that uploaded page images are high quality for accurate results.
        - Review before downloading results.

        """)

        st.info("Need more help? Contact us at [praguna.20@cse.mrt.ac.lk](mailto:praguna.20@cse.mrt.ac.lk)")

          
                        

if __name__ == "__main__":
    main()
