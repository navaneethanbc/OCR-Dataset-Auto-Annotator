import cv2
from PIL import Image as PILImage
import numpy as np
import matplotlib.pyplot as plt
from pdf2image import convert_from_path
import fitz  # PyMuPDF
import pandas as pd
import uuid
import os
from text_converter import TextConverter
import uuid
import pandas as pd
import zipfile
from io import BytesIO
import shutil
from docuwarp.unwarp import Unwarp
# import pytesseract
# from pytesseract import Output


class Image:

    def __init__(self,cv2_img):
        self.image = cv2_img

    def allign_pdf_img_to_photo_img(self,photo_img, display=0):
        pdf_img = self.image
        # Step 1: Initialize SIFT detector
        sift = cv2.SIFT_create()

        # Step 2: Detect keypoints and descriptors
        keypoints_pdf, descriptors_pdf = sift.detectAndCompute(pdf_img, None)
        keypoints_photo, descriptors_photo = sift.detectAndCompute(photo_img, None)

        # Step 3: Match descriptors using KNN and apply ratio test
        bf = cv2.BFMatcher()
        matches = bf.knnMatch(descriptors_pdf, descriptors_photo, k=2)

        # Apply ratio test to retain good matches
        good_matches = []
        for m, n in matches:
            if m.distance < 0.75 * n.distance:  # Lowe's ratio test
                good_matches.append(m)

        # Step 4: Select matched keypoints
        if len(good_matches) > 10:  # Minimum matches threshold
            src_pts = np.float32([keypoints_pdf[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
            dst_pts = np.float32([keypoints_photo[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)

            # Step 5: Find homography matrix with RANSAC
            matrix, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
            
            # Step 6: Warp the PDF image to align with the photo
            height, width = photo_img.shape
            aligned_pdf_img = cv2.warpPerspective(pdf_img, matrix, (width, height))

            # Step 7: Display both images side by side
            if display:
                plt.figure(figsize=(12, 6))
                
                # Original PDF Image
                plt.subplot(1, 2, 1)
                plt.imshow(photo_img, cmap='gray')
                plt.title("Photo image")
                plt.axis("off")
                
                # Aligned PDF Image
                plt.subplot(1, 2, 2)
                plt.imshow(aligned_pdf_img, cmap='gray')
                plt.title("Aligned PDF Image")
                plt.axis("off")
                
                plt.show()
        else:
            print("Not enough good matches to compute homography.")
        return aligned_pdf_img, matrix
    
    def deskew(self):
        gray = self.image
        # Find all non-zero pixel coordinates
        coords = np.column_stack(np.where(gray > 0))
        # Compute the angle of the minimum area rectangle around the text
        angle = cv2.minAreaRect(coords)[-1]
        
        # Adjust angle for small rotation
        if -10 < angle < 10:
            angle = -angle
        else:
            angle = 0  # Skip if angle is negligible or uncertain

        # Get the image dimensions
        (h, w) = gray.shape[:2]
        # Calculate the rotation matrix only if needed
        if angle != 0:
            M = cv2.getRotationMatrix2D((w // 2, h // 2), angle, 1.0)
            # Perform the affine transformation (rotation)
            deskewed = cv2.warpAffine(gray, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
            return deskewed
        else:
            # Return original image if no rotation is needed
            return gray

    def crop(self, bbox, pl=0, pr=0, pt=0, pb=0):
        photo_img = self.image
            
        x, y, w, h = bbox
        # Apply padding and ensure coordinates are within the image bounds
        x_start = max(int(x - pl), 0)
        y_start = max(int(y - pb), 0)
        x_end = min(int(x + w + pr), photo_img.shape[1])
        y_end = min(int(y + h + pt), photo_img.shape[0])

        # Crop the aligned image with padding around the bounding box
        cropped_img = photo_img[y_start:y_end, x_start:x_end]

        return cropped_img
    
    def unwarp(self):
        """
        Unwarps image using UVDoc method(paper).
        """
        unwarp = Unwarp()
        # Convert OpenCV image to PIL Image for compatibility
        # Downscale large images to reduce memory usage during unwarp
        img_bgr = self.image
        h, w = img_bgr.shape[:2]
        max_side = max(h, w)
        target_max = 2000  # cap largest side to this many pixels
        if max_side > target_max:
            scale = target_max / float(max_side)
            new_w = max(1, int(w * scale))
            new_h = max(1, int(h * scale))
            img_bgr = cv2.resize(img_bgr, (new_w, new_h), interpolation=cv2.INTER_AREA)

        pil_image = PILImage.fromarray(cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB))

        # Prepare input using Unwarp instance
        resized_input, original_input, original_size = unwarp.prepare_input(pil_image)

        # Perform inference
        points, _ = unwarp.session.run(None, {"input": resized_input.astype(np.float32)})

        # Ensure img_size is int64
        img_size = np.array(original_size).astype(np.int64)

        # Perform bilinear unwarping
        unwarped = unwarp.bilinear_unwarping.run(
            None,
            {
                "warped_img": original_input.astype(np.float32),
                "point_positions": points.astype(np.float32),
                "img_size": img_size,
            },
        )[0][0]

        # Convert unwarped result back to an image
        unwarped_image = PILImage.fromarray((unwarped.transpose(1, 2, 0) * 255).astype(np.uint8))
        if not isinstance(unwarped_image, np.ndarray):
            unwarped_image = np.array(unwarped_image)
        unwarped_image_cv2 = cv2.cvtColor(unwarped_image, cv2.COLOR_RGB2BGR)

        return unwarped_image_cv2
       

class utills:

    def __init__(self):
        pass

    
    # Function to create a custom horizontal kernel to detect lines
    @staticmethod
    def _horizontal_kernel(width):
        return np.ones((1, width), np.uint8)  # Create a 1-row kernel with a wide width

    # Function to get bounding boxes for lines
    @staticmethod
    def findLines(full_image):
        x_pad = 15
        y_pad = 7
        # Convert to grayscale and threshold the image
        gray = full_image #cv2.cvtColor(full_image, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)
        # Use a horizontal kernel to close gaps between words and detect full lines
        kernel = utills._horizontal_kernel(50)  # Adjust the width as needed
        closed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

        # Find contours of the closed image, expecting full lines to be detected
        contours, hierarchy = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        lines = []
        for cnt in contours:
            if cv2.contourArea(cnt) > 5:  # Adjust threshold to eliminate small artifacts
                x, y, w, h = cv2.boundingRect(cnt)
                lines.append([x-x_pad, y-y_pad, w+x_pad*2, h+y_pad*2])
        return lines[::-1]
    # @staticmethod
    # def findLinesTesseract(full_image):
    #     x_pad = 0
    #     y_pad = 0
    #     gray = full_image
    #     # Use Tesseract to detect text lines
    #     results = pytesseract.image_to_data(gray, output_type=Output.DICT)

    #     lines = []

    #     # Iterate through detected elements to find line-level data
    #     for i in range(len(results['level'])):
    #         if results['level'][i] == 4:  # Level 4 corresponds to lines
    #             x = results['left'][i]
    #             y = results['top'][i]
    #             w = results['width'][i]
    #             h = results['height'][i]

    #             # Apply padding and append the line bbox to the list
    #             lines.append([x - x_pad, y - y_pad, w + x_pad * 2, h + y_pad * 2])

    #     # Reverse order of lines to match original function's behavior
    #     return lines[::-1]

    # Function to transform a bounding box from aligned PDF image back to original PDF coordinates
    @staticmethod
    def inverse_transform_bbox(bbox, inverse_matrix):
        x, y, w, h = bbox
        pts = np.array([[x, y], [x + w, y], [x, y + h], [x + w, y + h]], dtype="float32").reshape(-1, 1, 2)
        original_pts = cv2.perspectiveTransform(pts, inverse_matrix)
        x_coords = original_pts[:, 0, 0]
        y_coords = original_pts[:, 0, 1]
        return (int(min(x_coords)), int(min(y_coords)), int(max(x_coords)), int(max(y_coords)))
    
    @staticmethod
    def invert_aligned_pdf_img_bboxes_to_original_pdf_img_bboxes(homography_matrix,line_bboxes_aligned_pdf):
        
        inverse_matrix = np.linalg.inv(homography_matrix)
        # Mapping bounding boxes from aligned image to original PDF coordinates
        mapped_bboxes = {}
        for bbox in line_bboxes_aligned_pdf:  # Start numbering from 1
            original_bbox = utills.inverse_transform_bbox(bbox, inverse_matrix)
            mapped_bboxes[tuple(bbox)] = original_bbox
        return mapped_bboxes
    

    
    # Function to transform and scale a bounding box from aligned PDF image back to original PDF coordinates
    @staticmethod
    def inverse_transform_and_scale_bbox(bbox, inverse_matrix, width_scale, height_scale):
        x, y, w, h = bbox
        pts = np.array([[x, y], [x + w, y], [x, y + h], [x + w, y + h]], dtype="float32").reshape(-1, 1, 2)
        original_pts = cv2.perspectiveTransform(pts, inverse_matrix)
        x_coords = original_pts[:, 0, 0] * width_scale
        y_coords = original_pts[:, 0, 1] * height_scale
        return (int(min(x_coords)), int(min(y_coords)), int(max(x_coords)), int(max(y_coords)))
    
    @staticmethod
    def extract_text_bbox_text_from_pdf(page,original_pdf_image_gray,line_bboxes_map_from_aligned_to_original_pdf,homography_matrix):

        # Load the PDF and get the first page (or any specific page if needed)
        

        # Get PDF page dimensions (width and height)
        pdf_width, pdf_height = page.rect.width, page.rect.height

        # Calculate scaling factors based on aligned image size and PDF page size
        aligned_img_height, aligned_img_width = original_pdf_image_gray.shape[:2]
        width_scale = pdf_width / aligned_img_width
        height_scale = pdf_height / aligned_img_height

        # Invert the homography matrix to go from aligned image back to original PDF
        inverse_matrix = np.linalg.inv(homography_matrix)

        bbox_to_unicode_dict ={}

        # Draw bounding boxes with scaling adjustment on the PDF
        for idx, aligned_pdf_bbox in enumerate(line_bboxes_map_from_aligned_to_original_pdf, 1):  # Start numbering from 1 # getting key of dictionary 
            # Transform and scale bounding box
            x0, y0, x1, y1 = utills.inverse_transform_and_scale_bbox(aligned_pdf_bbox, inverse_matrix, width_scale, height_scale)
            
            # Create a rectangle around the bounding box
            rect = fitz.Rect(x0, y0, x1, y1)
            text = page.get_text("text", clip=rect)
            unicode_text = TextConverter.convert_text_with_js(text.strip())
            # print("unicode_text",unicode_text)
            if unicode_text.splitlines():
                unicode_text=unicode_text.splitlines()[-1]
            else:
                continue
            # print(idx,unicode_text)
            bbox_to_unicode_dict[aligned_pdf_bbox] = unicode_text
            # print("------------------------")
            
            # Draw the rectangle on the page
            page.draw_rect(rect, color=(0, 1, 0), width=0.8)  # Green bounding box
            
            # Add label as text at the top-left corner of each bounding box
            label = f"BBox {idx}"
            page.insert_text((x0, y0 - 1), label, fontsize=8, color=(1, 0, 0))  # Red text

        # Save the modified PDF with bounding boxes
        # doc.save(output_pdf_path)
        # doc.close()

        # print(f"Saved the modified PDF with bounding boxes as {output_pdf_path}")
        # print(bbox_to_unicode_dict)
        return bbox_to_unicode_dict
    @staticmethod
    def create_result_zip(photo_img, segments, page_num):
        images = []
        texts = []
        output_dir = "./temp"
        os.makedirs(output_dir, exist_ok=True)
        shutil.rmtree(output_dir)
        img_dir = f"{output_dir}/images"
        os.makedirs(img_dir, exist_ok=True)
        line_count = len(segments)
        approved_text_corrected_line_count = 0
        approved_padding_corrected_line_count = 0
        rejected_line_count =0
        for segment in segments:
            if not segment["approved"]:
                rejected_line_count+=1
                continue
            if segment["text_corrected"]:
                approved_text_corrected_line_count+=1
            if segment["padding_corrected"]:
                approved_padding_corrected_line_count+=1
        
            cropped_img = Image(photo_img).crop(
            segment["bbox"],
            pl=segment["pl"],
            pr=segment["pr"],
            pt=segment["pt"],
            pb=segment["pb"])

            unique_filename = f"{uuid.uuid4().hex}.png"

            image_path = f"{img_dir}/{unique_filename}"
            cv2.imwrite(image_path, cropped_img)
            # print("Saving image to", image_path)

            images.append(unique_filename)
            # print("image",len(images))
            texts.append(segment["text"])
        approval_percantage = round((line_count-rejected_line_count)/line_count*100,2)
        approved_padding_or_text_corrected_line_count = max(approved_padding_corrected_line_count,approved_text_corrected_line_count)
        approval_without_editing_percentage = round((line_count-rejected_line_count-approved_padding_or_text_corrected_line_count)/line_count,2)
        # Save the DataFrame as a CSV
        df = pd.DataFrame({'image_name': images, 'Text': texts})
        csv_path = f"{output_dir}/page_{page_num}_annotation.csv"
        df.to_csv(csv_path, index=False, encoding='utf-8')

        # Create a ZIP file
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Add images to the ZIP file
            for img_file in images:
                img_path = f"{img_dir}/{img_file}"
                zip_file.write(img_path, arcname=f"page_{page_num}_images/{img_file}")

            # Add the CSV file to the ZIP file
            zip_file.write(csv_path, arcname=f"page_{page_num}_annotation(approved_{approval_percantage}% approved_without_editing_{approval_without_editing_percentage}%).csv")

        shutil.rmtree(output_dir)

        # Return ZIP buffer
        zip_buffer.seek(0)
        return zip_buffer

    @staticmethod
    def crop_and_save_img(photo_img, bbox_to_unicode_dict, padding,output_dir):
        
        images = []
        texts = []
        
        img_dir = f"{output_dir}"
        os.makedirs(img_dir, exist_ok=True)

        
        # Loop through each bounding box and display it individually with its text
        for idx, (bbox, text) in enumerate(bbox_to_unicode_dict.items(), 1):
            if len(text.split(" "))<=3:
                continue
            
            x, y, w, h = bbox
            # Apply padding and ensure coordinates are within the image bounds
            x_start = max(int(x - padding), 0)
            y_start = max(int(y - padding), 0)
            x_end = min(int(x + w + padding), photo_img.shape[1])
            y_end = min(int(y + h + padding), photo_img.shape[0])

            # Crop the aligned image with padding around the bounding box
            cropped_img = Image(photo_img).crop()

            unique_filename = f"{uuid.uuid4().hex}.png"

            image_path = f"{img_dir}/{unique_filename}"
            cv2.imwrite(image_path, cropped_img)
            # print("saving image to ",image_path)

            images.append(unique_filename)
            texts.append(text)
        
        df = pd.DataFrame({'image_name': images, 'Text': texts})
        return df

