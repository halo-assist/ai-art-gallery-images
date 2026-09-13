# kdp-kids-books — Etsy upload guide (for Long)

3 personalised name-book listings, ready to publish on the existing
QuietHueDesigns Etsy shop. Everything was built and verified by the pipeline;
only the upload + publish steps need you.

## Files
- `etsy_batch_import.csv` — 3 listings (Oliver, Charlotte, Amelia)
- `My_Name_Adventure_Book_<Name>.pdf` — the product file for each listing
  (A4, 19-20 pages, verified)
- `build_kids_name_book.py` + `lib.py` — generator for custom names (see below)

## Steps
1. Etsy Seller Dashboard → Listings → **Import listings** → upload
   `etsy_batch_import.csv`. This creates 3 drafts with titles, descriptions,
   tags, prices (AUD 8.95) and preview images (hosted URLs).
2. Open each draft and **attach the matching PDF**:
   - Oliver draft  ← `My_Name_Adventure_Book_Oliver.pdf`
   - Charlotte draft ← `My_Name_Adventure_Book_Charlotte.pdf`
   - Amelia draft  ← `My_Name_Adventure_Book_Amelia.pdf`
   (Etsy digital listings need the file attached to be downloadable.)
3. Confirm the **"Created with AI" / Designed-by** disclosure is ticked
   (description already contains the AI disclosure line).
4. Publish all 3.
5. Reply to the blocker email with the 3 listing URLs + publish date so the
   observation window (30 days, kill rule: 0 sales) can start.

## Custom name orders (free personalisation service)
The listings invite buyers to message for any other name. When an order comes in:
1. On this Mac, run:
   `python3 ~/idea_lab/scripts/build_kids_name_book.py "Isla" --out ~/Desktop`
   (any name, 2–12 letters; output: `My_Name_Adventure_Book_Isla.pdf`)
2. Open the Etsy order conversation, attach the generated PDF, and send it.
Same flow for spelling variants (e.g. "Caitlin" vs "Kaitlyn").

## Verification already done
- 19/20 pages each, every page exactly A4; page count matches HTML source 1:1
- Name appears on cover, belongs-to page, stars page, certificate + ≥3× on
  every story page; letter-hunt grid holds exactly 3 of each letter; maze path
  spells the name; certificate/maze headings present; no missing-glyph boxes
- Generator is deterministic (same name → identical output, byte-for-byte HTML)
- Preview images live at raw.githubusercontent.com/halo-assist/ai-art-gallery-images/
  main/kids-books/*_main.jpg (all HTTP 200)
