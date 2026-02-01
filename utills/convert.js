// Tamil Bamini -> Unicode converter using sequential text.replace (Sinhala-like structure)

const fmBaminiToUnicode = function (text) {
  // Order matters: apply longer sequences first
  // Decode literal \uXXXX sequences into actual Unicode first
  text = text.replace(/\\u([0-9A-Fa-f]{4})/g, (m, hex) => String.fromCharCode(parseInt(hex, 16)));
  // // Ensure micro sign maps explicitly regardless of editor encoding
  // text = text.replace(/\u00B5/g, "ர");
  // // Also map Greek small letter mu (U+03BC) if present
  // text = text.replace(/\u03BC/g, "ர");


  // Additional exact mappings (Eelam-style) provided
  // Ksha series
  text = text.replace(/ñõ/g, "க்ஷா");
  text = text.replace(/öñÍ/g, "க்ஷௌ");
  text = text.replace(/÷ñõ/g, "க்ஷோ");
  text = text.replace(/öñõ/g, "க்ஷொ");
  text = text.replace(/øñ/g, "க்ஷை");
  text = text.replace(/öñ/g, "க்ஷெ");
  text = text.replace(/÷ñ/g, "க்ஷே");
  text = text.replace(/ñü/g, "க்ஷூ");
  text = text.replace(/ñú/g, "க்ஷு");
  text = text.replace(/ó/g, "க்ஷீ");
  text = text.replace(/ò/g, "க்ஷி");
  text = text.replace(/ô/g, "க்ஷ்");
  text = text.replace(/ñ/g, "க்ஷ");

  // Ja series
  text = text.replace(/öáÍ/g, "ஜௌ");
  text = text.replace(/÷áõ/g, "ஜோ");
  text = text.replace(/öáõ/g, "ஜொ");
  text = text.replace(/øá/g, "ஜை");
  text = text.replace(/öá/g, "ஜெ");
  text = text.replace(/÷á/g, "ஜே");
  text = text.replace(/áü/g, "ஜூ");
  text = text.replace(/áú/g, "ஜு");
  text = text.replace(/ã/g, "ஜீ");
  text = text.replace(/â/g, "ஜி");
  text = text.replace(/ä/g, "ஜ்");
  text = text.replace(/áõ/g, "ஜா");
  text = text.replace(/á/g, "ஜ");

  // Ka series
  text = text.replace(/öPÍ/g, "கௌ");
  text = text.replace(/÷Põ/g, "கோ");
  text = text.replace(/öPõ/g, "கொ");
  text = text.replace(/øP/g, "கை");
  text = text.replace(/öP/g, "கெ");
  text = text.replace(/÷P/g, "கே");
  text = text.replace(/T/g, "கூ");
  text = text.replace(/S/g, "கு");
  text = text.replace(/R/g, "கீ");
  text = text.replace(/Q/g, "கி");
  text = text.replace(/U/g, "க்");
  text = text.replace(/Põ/g, "கா");
  text = text.replace(/P/g, "க");

  // Nga series
  text = text.replace(/öVÍ/g, "ஙௌ");
  text = text.replace(/÷Võ/g, "ஙோ");
  text = text.replace(/öVõ/g, "ஙொ");
  text = text.replace(/øV/g, "ஙை");
  text = text.replace(/öV/g, "ஙெ");
  text = text.replace(/÷V/g, "ஙே");
  text = text.replace(/Z/g, "ஙூ");
  text = text.replace(/Y/g, "ஙு");
  text = text.replace(/X/g, "ஙீ");
  text = text.replace(/W/g, "ஙி");
  text = text.replace(/\[/g, "ங்");
  text = text.replace(/Võ/g, "ஙா");
  text = text.replace(/V/g, "ங");

  // Sa series
  text = text.replace(/ö\\Í/g, "சௌ");
  text = text.replace(/÷\\õ/g, "சோ");
  text = text.replace(/ö\\õ/g, "சொ");
  text = text.replace(/ø\\/g, "சை");
  text = text.replace(/ö\\/g, "செ");
  text = text.replace(/÷\\/g, "சே");
  text = text.replace(/`/g, "சூ");
  text = text.replace(/_/g, "சு");
  text = text.replace(/\^/g, "சீ");
  text = text.replace(/]/g, "சி");
  text = text.replace(/a/g, "ச்");
  text = text.replace(/\\õ/g, "சா");
  text = text.replace(/\\/g, "ச");

  // Nya series
  text = text.replace(/öbÍ/g, "ஞௌ");
  text = text.replace(/÷bõ/g, "ஞோ");
  text = text.replace(/öbõ/g, "ஞொ");
  text = text.replace(/øb/g, "ஞை");
  text = text.replace(/öb/g, "ஞெ");
  text = text.replace(/÷b/g, "ஞே");
  text = text.replace(/f/g, "ஞூ");
  text = text.replace(/e/g, "ஞு");
  text = text.replace(/d/g, "ஞீ");
  text = text.replace(/c/g, "ஞி");
  text = text.replace(/g/g, "ஞ்");
  text = text.replace(/bõ/g, "ஞா");
  text = text.replace(/b/g, "ஞ");

  // Ta series
  text = text.replace(/öhÍ/g, "டௌ");
  text = text.replace(/÷hõ/g, "டோ");
  text = text.replace(/öhõ/g, "டொ");
  text = text.replace(/øh/g, "டை");
  text = text.replace(/öh/g, "டெ");
  text = text.replace(/÷h/g, "டே");
  text = text.replace(/l/g, "டூ");
  text = text.replace(/k/g, "டு");
  text = text.replace(/j/g, "டீ");
  text = text.replace(/i/g, "டி");
  text = text.replace(/m/g, "ட்");
  text = text.replace(/hõ/g, "டா");
  text = text.replace(/h/g, "ட");

  // Nna series
  text = text.replace(/önÍ/g, "ணௌ");
  text = text.replace(/÷nõ/g, "ணோ");
  text = text.replace(/önõ/g, "ணொ");
  text = text.replace(/øn/g, "ணை");
  text = text.replace(/ön/g, "ணெ");
  text = text.replace(/÷n/g, "ணே");
  text = text.replace(/r/g, "ணூ");
  text = text.replace(/q/g, "ணு");
  text = text.replace(/p/g, "ணீ");
  text = text.replace(/o/g, "ணி");
  text = text.replace(/s/g, "ண்");
  text = text.replace(/nõ/g, "ணா");
  text = text.replace(/n/g, "ண");

  // Tha series
  text = text.replace(/öuÍ/g, "தௌ");
  text = text.replace(/÷uõ/g, "தோ");
  text = text.replace(/öuõ/g, "தொ");
  text = text.replace(/øu/g, "தை");
  text = text.replace(/öu/g, "தெ");
  text = text.replace(/÷u/g, "தே");
  text = text.replace(/y/g, "தூ");
  text = text.replace(/x/g, "து");
  text = text.replace(/w/g, "தீ");
  text = text.replace(/v/g, "தி");
  text = text.replace(/z/g, "த்");
  text = text.replace(/uõ/g, "தா");
  text = text.replace(/u/g, "த");

  // Na series
  text = text.replace(/ö\|Í/g, "நௌ");
  text = text.replace(/÷\|õ/g, "நோ");
  text = text.replace(/ö\|õ/g, "நொ");
  text = text.replace(/ø\|/g, "நை");
  text = text.replace(/ö\|/g, "நெ");
  text = text.replace(/÷\|/g, "நே");
  text = text.replace(/¡/g, "நூ");
  text = text.replace(/~/g, "நு");
  text = text.replace(/}/g, "நீ");
  text = text.replace(/\{/g, "நி");
  text = text.replace(/¢/g, "ந்");
  text = text.replace(/\|õ/g, "நா");
  text = text.replace(/\|/g, "ந");

  // Nna (na) series
  text = text.replace(/öÚÍ/g, "னௌ");
  text = text.replace(/÷Úõ/g, "னோ");
  text = text.replace(/öÚõ/g, "னொ");
  text = text.replace(/øÚ/g, "னை");
  text = text.replace(/öÚ/g, "னெ");
  text = text.replace(/÷Ú/g, "னே");
  text = text.replace(/Þ/g, "னூ");
  text = text.replace(/Ý/g, "னு");
  text = text.replace(/Ü/g, "னீ");
  text = text.replace(/Û/g, "னி");
  text = text.replace(/ß/g, "ன்");
  text = text.replace(/Úõ/g, "னா");
  text = text.replace(/Ú/g, "ன");

  // Pa series
  text = text.replace(/ö£Í/g, "பௌ");
  text = text.replace(/÷£õ/g, "போ");
  text = text.replace(/ö£õ/g, "பொ");
  text = text.replace(/ø£/g, "பை");
  text = text.replace(/ö£/g, "பெ");
  text = text.replace(/÷£/g, "பே");
  text = text.replace(/§/g, "பூ");
  text = text.replace(/¦/g, "பு");
  text = text.replace(/¥/g, "பீ");
  text = text.replace(/¤/g, "பி");
  text = text.replace(/¨/g, "ப்");
  text = text.replace(/£õ/g, "பா");
  text = text.replace(/£/g, "ப");

  // Ma series
  text = text.replace(/ö©Í/g, "மௌ");
  text = text.replace(/÷©õ/g, "மோ");
  text = text.replace(/ö©õ/g, "மொ");
  text = text.replace(/ø©/g, "மை");
  text = text.replace(/ö©/g, "மெ");
  text = text.replace(/÷©/g, "மே");
  text = text.replace(/‰/g, "மூ");
  text = text.replace(/•/g, "மு");
  text = text.replace(/«/g, "மீ");
  text = text.replace(/ª/g, "மி");
  text = text.replace(/®/g, "ம்");
  text = text.replace(/©õ/g, "மா");
  text = text.replace(/©/g, "ம");

  // Ya series
  text = text.replace(/ö¯Í/g, "யௌ");
  text = text.replace(/÷¯õ/g, "யோ");
  text = text.replace(/ö¯õ/g, "யொ");
  text = text.replace(/ø¯/g, "யை");
  text = text.replace(/ö¯/g, "யெ");
  text = text.replace(/÷¯/g, "யே");
  text = text.replace(/³/g, "யூ");
  text = text.replace(/²/g, "யு");
  text = text.replace(/±/g, "யீ");
  text = text.replace(/°/g, "யி");
  text = text.replace(/´/g, "ய்");
  text = text.replace(/¯õ/g, "யா");
  text = text.replace(/¯/g, "ய");

  // Ra series
  text = text.replace(/öµÍ/g, "ரௌ");
  text = text.replace(/÷µõ/g, "ரோ");
  text = text.replace(/öµõ/g, "ரொ");
  text = text.replace(/øµ/g, "ரை");
  text = text.replace(/öµ/g, "ரெ");
  text = text.replace(/÷µ/g, "ரே");
  text = text.replace(/¹/g, "ரூ");
  text = text.replace(/¸/g, "ரு");
  text = text.replace(/Ÿ/g, "ரீ");
  text = text.replace(/›/g, "ரி");
  text = text.replace(/º/g, "ர்");
  text = text.replace(/µõ/g, "ரா");
  text = text.replace(/µ/g, "ர");

  // La series
  text = text.replace(/ö»Í/g, "லௌ");
  text = text.replace(/÷»õ/g, "லோ");
  text = text.replace(/ö»õ/g, "லொ");
  text = text.replace(/ø»/g, "லை");
  text = text.replace(/ö»/g, "லெ");
  text = text.replace(/÷»/g, "லே");
  text = text.replace(/¿/g, "லூ");
  text = text.replace(/¾/g, "லு");
  text = text.replace(/½/g, "லீ");
  text = text.replace(/¼/g, "லி");
  text = text.replace(/À/g, "ல்");
  text = text.replace(/»õ/g, "லா");
  text = text.replace(/»/g, "ல");

  // Lla series
  text = text.replace(/öÍÍ/g, "ளௌ");
  text = text.replace(/÷Íõ/g, "ளோ");
  text = text.replace(/öÍõ/g, "ளொ");
  text = text.replace(/øÍ/g, "ளை");
  text = text.replace(/öÍ/g, "ளெ");
  text = text.replace(/÷Í/g, "ளே");
  text = text.replace(/Ñ/g, "ளூ");
  text = text.replace(/Ð/g, "ளு");
  text = text.replace(/Ï/g, "ளீ");
  text = text.replace(/Î/g, "ளி");
  text = text.replace(/Ò/g, "ள்");
  text = text.replace(/Íõ/g, "ளா");
  text = text.replace(/Í/g, "ள");

  // Va series
  text = text.replace(/öÁÁ/g, "வௌ");
  text = text.replace(/÷Áõ/g, "வோ");
  text = text.replace(/öÁõ/g, "வொ");
  text = text.replace(/øÁ/g, "வை");
  text = text.replace(/öÁ/g, "வெ");
  text = text.replace(/÷Á/g, "வே");
  text = text.replace(/Å/g, "வூ");
  text = text.replace(/Ä/g, "வு");
  text = text.replace(/Ã/g, "வீ");
  text = text.replace(/Â/g, "வி");
  text = text.replace(/Æ/g, "வ்");
  text = text.replace(/Áõ/g, "வா");
  text = text.replace(/Á/g, "வ");

  // Zha series
  text = text.replace(/öÇÇ/g, "ழௌ");
  text = text.replace(/÷Çõ/g, "ழோ");
  text = text.replace(/öÇõ/g, "ழொ");
  text = text.replace(/øÇ/g, "ழை");
  text = text.replace(/öÇ/g, "ழெ");
  text = text.replace(/÷Ç/g, "ழே");
  text = text.replace(/Ë/g, "ழூ");
  text = text.replace(/Ê/g, "ழு");
  text = text.replace(/É/g, "ழீ");
  text = text.replace(/È/g, "ழி");
  text = text.replace(/Ì/g, "ழ்");
  text = text.replace(/Çõ/g, "ழா");
  text = text.replace(/Ç/g, "ழ");

  // Rra series
  text = text.replace(/öÓÓ/g, "றௌ");
  text = text.replace(/÷Óõ/g, "றோ");
  text = text.replace(/öÓõ/g, "றொ");
  text = text.replace(/øÓ/g, "றை");
  text = text.replace(/öÓ/g, "றெ");
  text = text.replace(/÷Ó/g, "றே");
  text = text.replace(/Ö/g, "று");
  text = text.replace(/Õ/g, "றீ");
  text = text.replace(/Ô/g, "றி");
  text = text.replace(/Ø/g, "ற்");
  text = text.replace(/Óõ/g, "றா");
  text = text.replace(/Ó/g, "ற");

  // Ha series
  text = text.replace(/öíí/g, "ஹௌ");
  text = text.replace(/÷íõ/g, "ஹோ");
  text = text.replace(/öíõ/g, "ஹொ");
  text = text.replace(/øí/g, "ஹை");
  text = text.replace(/öí/g, "ஹெ");
  text = text.replace(/÷í/g, "ஹே");
  text = text.replace(/íü/g, "ஹூ");
  text = text.replace(/íú/g, "ஹு");
  text = text.replace(/ï/g, "ஹீ");
  text = text.replace(/î/g, "ஹி");
  text = text.replace(/ð/g, "ஹ்");
  text = text.replace(/íõ/g, "ஹா");
  text = text.replace(/í/g, "ஹ");

  // Sha series
  text = text.replace(/öåå/g, "ஷௌ");
  text = text.replace(/÷åõ/g, "ஷோ");
  text = text.replace(/öåõ/g, "ஷொ");
  text = text.replace(/øå/g, "ஷை");
  text = text.replace(/öå/g, "ஷெ");
  text = text.replace(/÷å/g, "ஷே");
  text = text.replace(/åü/g, "ஷூ");
  text = text.replace(/åú/g, "ஷு");
  text = text.replace(/ç/g, "ஷீ");
  text = text.replace(/æ/g, "ஷி");
  text = text.replace(/è/g, "ஷ்");
  text = text.replace(/åõ/g, "ஷா");
  text = text.replace(/å/g, "ஷ");

  // Sa (ஸ) series
  text = text.replace(/öéே/g, "ஸே");
  text = text.replace(/öéé/g, "ஸௌ");
  text = text.replace(/÷éõ/g, "ஸோ");
  text = text.replace(/öéõ/g, "ஸொ");
  text = text.replace(/øé/g, "ஸை");
  text = text.replace(/öé/g, "ஸெ");
  text = text.replace(/÷é/g, "ஸே");
  text = text.replace(/éü/g, "ஸூ");
  text = text.replace(/éú/g, "ஸு");
  text = text.replace(/ë/g, "ஸீ");
  text = text.replace(/ê/g, "ஸி");
  text = text.replace(/ì/g, "ஸ்");
  text = text.replace(/éõ/g, "ஸா");
  text = text.replace(/é/g, "ஸ");

  // Independent vowels and others
  text = text.replace(/JÍ/g, "ஔ");
  text = text.replace(/K/g, "ஓ");
  text = text.replace(/J/g, "ஒ");
  text = text.replace(/I/g, "ஐ");
  text = text.replace(/H/g, "ஏ");
  text = text.replace(/G/g, "எ");
  text = text.replace(/F/g, "ஊ");
  text = text.replace(/E/g, "உ");
  text = text.replace(/D/g, "ஈ");
  text = text.replace(/C/g, "இ");
  text = text.replace(/B/g, "ஆ");
  text = text.replace(/A/g, "அ");
  text = text.replace(/L/g, "ஃ");
  text = text.replace(/ÿ/g, "ஸ்ரீ");
  text = text.replace(/&/g, "-");
  text = text.replace(/-/g, "");

  return text;
}

const inputText = process.argv[2];
console.log(fmBaminiToUnicode(inputText));
  