# Unified Taxonomy Review: Tensions, Coordinate Clashes & Expansion Plan

Branch: `unified-taxonomy`

This document tracks all identified tensions, conflicting data coordinates across **Format**, **Element**, **Sound**, and **Colour**, cross-ontology interactions, and candidate expansions across the FIAFcore ontology (`ontology/*.ttl`) and the three archive mappings (**BFI**, **Bundesarchiv**, and **NB / National Library of Norway**).

Each item has a **Status** and **Resolution** block so decisions can be worked through point by point across sessions and documented alongside the code and `TAXONOMY_OVERVIEW.md`.

---

## Part 1: Colour Taxonomy & Mappings

### 1.1 Applied Colour Processes (`Tinted`, `Toned`, `HandColouring`, `StencilColouring`) vs. `BlackAndWhite`
- **Status**: **RESOLVED**
- **Issue**:
  - `TAXONOMY_OVERVIEW.md` (Examples 1 & 3), `example/Item.ttl`, `bundesarchiv.xsl`, `BFI_FIAF_LOD_Items.xsl`, and `BFI_FIAF_LOD_Manifestations.xsl` previously paired applied colour processes (`fiaf:Tinted`, `fiaf:Toned`, `fiaf:HandColouring`, `fiaf:StencilColouring`) with `a fiaf:BlackAndWhite` on the `ColourCharacteristic` blank node, even when the item is purely tinted/toned/coloured and not black-and-white in appearance.
  - Meanwhile, `BFI_FIAF_LOD_Manifestations.xsl` paired `Pathécolor` (`StencilColouring`) with `a fiaf:Colour` when `$colour_manifestation = 'Colour'`, creating an inconsistency between Manifestation and Item levels.
- **Resolution**:
  - **`fiaf:BlackAndWhite` is used only when the moving image is actually black and white in appearance** (or has untinted/untoned black-and-white sequences alongside coloured sequences, such as `'BW and Tinted Positive'`).
  - When an Item or Manifestation only has an applied colour process (`Tinted`, `Toned`, `HandColouring`, `StencilColouring`), it is sufficient to state `[ fiaf:hasColourProcess fiaf:Tinted ]` on the `ColourCharacteristic` blank node without asserting `a fiaf:BlackAndWhite` or `a fiaf:Colour`.
  - If an item has both black-and-white and tinted/toned sequences (e.g., BFI `'BW and Tinted Positive'`), emit separate `ColourCharacteristic` blank nodes (`[ a fiaf:BlackAndWhite ], [ fiaf:hasColourProcess fiaf:Tinted ]`) or include `BlackAndWhite` only when `'BW'` is explicitly stated.
- **Affected Files** *(all updated)*:
  - `TAXONOMY_OVERVIEW.md` (Core Design Principle 1, Example 1, Example 3)
  - `example/Item.ttl` (lines 25–29: `<https://example.fiafcore.org/tinted-item>`)
  - `transform/bundesarchiv/xsl/bundesarchiv.xsl` (lines 1857–1943: `Schablonenkolorierung`, `Handkolorierung`, `Virage`, `Tonung`, `Virage und Tonung`)
  - `transform/bfi/xsl/BFI_FIAF_LOD_Items.xsl` (lines 69–107: `BlackAndWhite` no longer emitted merely because `'Tinted'`, `'Toned'`, `'Sepia'`, or `'Stencil'` is present)
  - `transform/bfi/xsl/BFI_FIAF_LOD_Manifestations.xsl` (lines 84–89 & 289–291: `BlackAndWhite` removed from `Sepia`, duplicate `Toned` block removed)

---

### 1.2 Colour Separation Elements & Dye-Transfer Matrices (`ColourSeparationNegative`, `ColourSeparationPositive`, `DyeTransferMatrix`)
- **Status**: **RESOLVED**
- **Issue**:
  - In `transform/bfi/xsl/BFI_FIAF_LOD_Items.xsl` (lines 71–104):
    - Separation records (`'Cyan Separation Negative'`, `'Yellow Separation Promaster'`, `'Original Red Separation Negative'`), successive-frame separations (`'Successive frame Separation Negative'`, `'Successive frame Promaster'`), and dye-transfer matrices (`'Cyan Separation Matrix'`, `'Yellow Matrix'`) were previously assigned `ColourStandard` processes (`fiaf:ColourSeparation`, `fiaf:PrintingDyeTransferPigment`, `fiaf:TemporalSynthesis`) and inconsistent `BlackAndWhite` / `Colour` types.
    - Physically, colour separation negatives, separation positives/promasters, and dye-transfer relief matrices are monochrome (`fiaf:BlackAndWhite`) intermediate elements that can only produce a colour image when recombined in printing or scanning; they are specialized `Element` types rather than colour-appearance processes on the separation item itself.
- **Resolution**:
  - Added three dedicated `Element` subclasses in `ontology/fiafcore-element.ttl`:
    - `fiaf:ColourSeparationNegative` (`rdfs:subClassOf fiaf:Negative`)
    - `fiaf:ColourSeparationPositive` (`rdfs:subClassOf fiaf:Positive`)
    - `fiaf:DyeTransferMatrix` (`rdfs:subClassOf fiaf:Positive`)
  - On `fiaf:hasColourCharacteristic`, all separation records, successive-frame separation records, and dye-transfer matrices emit `[ a fiaf:BlackAndWhite ]` without a `hasColourProcess` property.
  - On `fiaf:isElement`, separation negatives (`'... Separation Negative'`, `'Successive frame ... Negative'`, `'Tri Negative'`) map to `fiaf:ColourSeparationNegative`; separation positives and separation protection masters (`'... Separation Positive'`, `'... Separation Promaster'`, `'Successive frame ... Promaster'`) map to `fiaf:ColourSeparationPositive`; and dye-transfer matrices (`'... Matrix'`) map to `fiaf:DyeTransferMatrix`.
- **Affected Files** *(all updated)*:
  - `ontology/fiafcore-element.ttl`
  - `vocabulary/fiafcore-element.ttl` & `fiafcore.ttl` (regenerated via `uv run compile.py`)
  - `transform/bfi/xsl/BFI_FIAF_LOD_Items.xsl`

---

### 1.3 Unmatched Colour Names in BFI `<physical_description>`
- **Status**: **RESOLVED**
- **Issue**:
  - BFI `<physical_description>` includes shorthand separation strings without the word `'Separation'` (`'Cyan/Magenta/Yellow Promaster'`, `'Cyan/Magenta Colour Promaster'`, `'Master Cyan Promaster'`, `'Cyan/Magenta/Yellow/Red/Blue Negative'`, `'Dupe Blue/Magenta/Red Negative'`, `'Magenta Colour Negative'`), polarity-unspecified separation strings (`'Cyan/Magenta/Yellow Separation'`, `'Dupe Cyan Separation'`, `'Master Cyan/Magenta/Yellow Separation'`, `'Master Separation'`), and bare colour-named positives (`'Blue Positive'`, `'Magenta Positive'`, `'Orange BW Positive'`, `'Yellow BW Positive'`, `'Cyan BW Positive'`, `'Blue BW Positive'`, `'Magenta BW Positive'`).
- **Resolution**:
  - Shorthand CMY/RGB separation negatives (`'Cyan/Magenta/Yellow/Red/Blue Negative'`, `'Dupe Blue/Magenta/Red Negative'`, `'Magenta Colour Negative'`) map to `fiaf:isElement fiaf:ColourSeparationNegative` and `fiaf:hasColourCharacteristic [ a fiaf:BlackAndWhite ]`.
  - Shorthand CMY protection master positives (`'Cyan/Magenta/Yellow Promaster'`, `'Cyan/Magenta Colour Promaster'`, `'Master Cyan Promaster'`) map to `fiaf:isElement fiaf:ColourSeparationPositive` and `fiaf:hasColourCharacteristic [ a fiaf:BlackAndWhite ]`.
  - Polarity-unspecified separation strings (`'Cyan/Magenta/Yellow Separation'`, `'Dupe Cyan Separation'`, `'Master Cyan/Magenta/Yellow Separation'`, `'Master Separation'`) map to `fiaf:isElement fiaf:FilmElement` and `fiaf:hasColourCharacteristic [ a fiaf:BlackAndWhite ]` (matching `'Separation Negative and Positive'`).
  - Bare colour-named positives without `'Tinted'`, `'Toned'`, or `'Separation'` (`'Blue Positive'`, `'Orange BW Positive'`, etc.) do not guess a colour process; they emit `BlackAndWhite` only when `'BW'` is present and `Colour` only when `'Colour'` is present.
- **Affected Files** *(all updated)*:
  - `transform/bfi/xsl/BFI_FIAF_LOD_Items.xsl`

---

### 1.4 Digital Scans of Photochemically Coloured / Tinted Films
- **Status**: **RESOLVED**
- **Issue**:
  - `TAXONOMY_OVERVIEW.md` Principle 1 states: *"A tinted nitrate print has `fiaf:hasColourProcess fiaf:Tinted`; a digital preservation scan of that print describes its digital pixel representation (`fiaf:hasColourEncoding fiaf:RGB`, `fiaf:hasColourSpace fiaf:ACES2065_1`, `fiaf:hasTransferFunction fiaf:Linear`), not photochemical tinting."*
  - However, if a digital Item is an RGB scan of a tinted/toned print:
    - Its pixel encoding is `fiaf:RGB` (or `fiaf:YUV`), not `fiaf:Greyscale`.
    - What should the digital Item's `ColourCharacteristic` blank node look like, and should photochemical `hasColourProcess` ever appear on a digital scan `Item`?
- **Resolution**:
  - **Strict separation**: Digital scan `Item`s only carry digital colour properties (`hasColourEncoding`, `hasColourSpace`, `hasTransferFunction`) and never `hasColourProcess` (photochemical processes belong on the photochemical `Item` or `Manifestation`).
  - **Consistent `BlackAndWhite` / `Colour` typing (View B)**: Just as a tinted/toned film print omits `a fiaf:BlackAndWhite` and `a fiaf:Colour`, a digital scan of an applied-colour print carries `[ fiaf:hasColourEncoding fiaf:RGB ; fiaf:hasColourSpace fiaf:ACES2065_1 ; fiaf:hasTransferFunction fiaf:Linear ]` without asserting `a fiaf:BlackAndWhite` or `a fiaf:Colour` (whereas scans of B&W films include `a fiaf:BlackAndWhite` and scans of natural/mimetic colour films include `a fiaf:Colour`). The named colour space is illustrative, not inferred from the scan's source material.
- **Affected Files** *(all updated)*:
  - `TAXONOMY_OVERVIEW.md` (Core Design Principle 1)

---

### 1.5 Specific ACES Colour Space Rather Than the ACES System
- **Status**: **RESOLVED**
- **Decision**: Replace the unused broad ACES term with `fiaf:ACES2065_1`, labelled "ACES2065-1 (AP0)". Remove the old IRI rather than retaining a deprecated alias, as explicitly agreed. Existing illustrative examples now use the specific colour space; no observed source mapping is assumed to identify ACES2065-1.
- **Rationale**: ACES is a colour-management system containing multiple encodings/spaces. ACES2065-1 identifies AP0 primaries, the ACES white point, and scene-linear RGB, so it can be described using the existing ColourSpace, ColourEncoding (RGB), and TransferFunction (Linear) properties. These are separate descriptive aspects, not arbitrary independent choices. No general ACES taxonomy expansion is needed.
- **Usage check**: The SPARQL page at `https://dev.fiafcore.org/sparql` identifies `https://data.fiafcore.org` as its endpoint. An exact-IRI query for the old term in subject, predicate, and object positions returned no matches in the currently served dataset. Local references were the ontology/generated vocabulary and illustrative documentation, not source transforms. This check does not establish usage outside that dataset.
- **Source**: [Official ACES2065-1 specification](https://docs.acescentral.com/encodings/aces2065-1/), referencing SMPTE ST 2065-1.
- **Unchanged**: Historical colour-process meanings and IRIs; flexibility to combine processes on one characteristic node. Ordering and precise sequence coverage remain outside this model, for example in prose notes. Rec. 601/709/2020 labels are not changed by this decision.

---

## Part 2: Format & Element Taxonomy & Coordinate Clashes

### 2.1 Digital Objects (`DigitalFormat`) vs. Physical Data Carriers (`DataStorageFormat`) on `Item` and `Carrier`
- **Status**: **RESOLVED**
- **Issue**:
  - `TAXONOMY_OVERVIEW.md` Principle 4 separated file-level digital `Item`s (`DigitalFormat` + `DigitalElement`) from physical data carrier `Item`s (`DataStorageFormat`, e.g., `LTO5`, `HardDrive`, `MagnetoOpticalDisc`).
  - In **Bundesarchiv** (`bundesarchiv.xsl` lines 2001–2242), a single `ba:Exemplar` record has both `ba:Container` (e.g. `DPX`, `MXF`, `MOV`, `MP4`, `WAV`) and `ba:Aufbewahrungseinheit/ba:Materialart` (e.g. `LTO_5`, `HDD`, `Magnetic_Optical_Disc`). The XSLT emits **both** `fiaf:hasFormat fiaf:DPX` (`DigitalFormat`) and `fiaf:hasFormat fiaf:LTO5` (`DataStorageFormat`) on the **same `fiaf:Item`**.
  - In **NB** (`MAPPING.md` §6.8), `LTO-3`..`LTO-6`, `Harddisk`, `MO-disk`, `Minnebrikke/-penn` are recorded on `Item` (`Carrier_type/carrier_type_specific`), and format information can sit at both the `Item` level and the `Carrier` (`ITEM_PART`, e.g., 5 DPX reel sequences under a 5-reel film scan `Item`) level for searchability.
- **Resolution**:
  - Kept `fiaf:DataStorageFormat` (`LTO`, `LTO2`–`LTO6`, `HardDrive`, `MagnetoOpticalDisc`, `FlashMemory`) in `ontology/fiafcore-format.ttl` for archives that catalogue offline storage media as `Item`s or `Carrier`s (either alone when file contents are not fully catalogued, or alongside `DigitalFormat` on the same `Item` as in Bundesarchiv).
  - Expanded `rdfs:domain` of `fiaf:hasFormat` in `ontology/fiafcore-manifestation.ttl` to `[ owl:unionOf (Manifestation Item Carrier) ]` so format statements can be made at the `Manifestation`, `Item`, and `Carrier` (`ITEM_PART`) levels.
  - Updated `fiaf:Carrier`'s `dc:description` in `ontology/fiafcore-carrier.ttl` to explicitly include discrete **physical or digital** units/parts of an `Item` (e.g. individual film reels or per-reel digital file sequences).
  - *Note*: For the deeper architectural question of replacing `fiaf:Carrier` with recursive `fiaf:Item` whole–part relationships (`hasPart`/`isPartOf`) and modeling shared offline storage carriers (`LTO`, `HardDrive`) independently of `Work`/`Manifestation`, see **§4.8** and `CARRIER_AND_DIGITAL_MODELING.md`.
- **Affected Files** *(all updated)*:
  - `ontology/fiafcore-manifestation.ttl` (`fiaf:hasFormat` domain)
  - `ontology/fiafcore-carrier.ttl` (`fiaf:Carrier` description)
  - `fiafcore.ttl` (regenerated via `uv run compile.py`)
  - `TAXONOMY_OVERVIEW.md` (Core Design Principle 4)

---

### 2.2 Optical Video Discs: Dissolving `OpticalFormat` into `VideoFormat`, `AudioFormat`, and `DataStorageFormat`
- **Status**: **RESOLVED**
- **Issue**:
  - Previously, `fiafcore-format.ttl` grouped `DVD`, `BluRay`, `LaserDisc`, `VCD`, `SVCD`, and `CD` under `fiaf:OpticalFormat` (by laser-reading physics) rather than by functional modality (`VideoFormat`, `AudioFormat`, `DataStorageFormat`).
  - As a result, optical video discs (`DVD`, `BluRay`, `LaserDisc`) were outside `fiaf:VideoFormat` even though their elements (`HomeViewingCopy`, `VideoAccessCopy`) sat under `fiaf:VideoElement`, and recordable optical discs used for data storage (`CDR`, `DVDR`) were mixed with authored video/audio disc formats.
- **Resolution**:
  - Dissolved `fiaf:OpticalFormat` across the three functional branches in `ontology/fiafcore-format.ttl`:
    - **`fiaf:VideoFormat` → `fiaf:OpticalVideoDisc`**: `fiaf:BluRay` (and `fiaf:UltraHDBluRay`), `fiaf:DVD`, `fiaf:LaserDisc`, `fiaf:SVCD`, `fiaf:VCD`.
    - **`fiaf:AudioFormat`**: `fiaf:CD`.
    - **`fiaf:DataStorageFormat`**: `fiaf:CDR`, `fiaf:DVDR` (for recordable optical discs holding digital files, e.g. `.mp4`/`.mov` access files on a DVD-R).
- **Affected Files** *(all updated)*:
  - `ontology/fiafcore-format.ttl`
  - `vocabulary/fiafcore-format.ttl` & `fiafcore.ttl` (regenerated via `uv run compile.py`)
  - `FORMAT_TAXONOMY.md` & `TAXONOMY_OVERVIEW.md`

---

### 2.3 `16mmMagneticFilm` & `35mmMagneticFilm` When Gauge and Sepmag Are in Separate Fields
- **Status**: **RESOLVED**
- **Issue**:
  - `fiaf:16mmMagneticFilm` and `fiaf:35mmMagneticFilm` live under `fiaf:FilmFormat`, and `TAXONOMY_OVERVIEW.md` Example 4 shows a 35mm sepmag using `fiaf:hasFormat fiaf:35mmMagneticFilm` and `fiaf:isElement fiaf:SeparatedMagneticSound`.
  - However, in **Bundesarchiv** (`ba:Filmbreite = '35_mm'` + `ba:Materialart = 'Magnetband'`) and **NB** (`gauge = '35mm'` + `carrier_type_specific = 'Sepmag'`), film gauge is in a separate field from magnetic element type:
    - `ba:Filmbreite = '35_mm'` unconditionally emitted `fiaf:hasFormat fiaf:35mmFilm` (photochemical film) instead of `fiaf:35mmMagneticFilm`.
    - And in `bundesarchiv.xsl` (lines 2716, 2835), `Magnetband` and `Magnetband_zu_Farbe` mapped to generic `fiaf:AudioElement` rather than `fiaf:SeparatedMagneticSound`.
- **Resolution**:
  - Updated `bundesarchiv.xsl` (`ba:Filmbreite` block): when `ba:Aufbewahrungseinheit/ba:Materialart` is `'Magnetband'` or `'Magnetband_zu_Farbe'`, `'35_mm'` emits `fiaf:35mmMagneticFilm` and `'16_mm'` / `'16_mm_neue_Norm'` / `'16_mm_alte_Norm'` emits `fiaf:16mmMagneticFilm` (and `'6,25_mm'` maps to `fiaf:QuerterInchAudiotape`).
  - Updated `bundesarchiv.xsl` (`fiaf:isElement` block): `'Magnetband'` and `'Magnetband_zu_Farbe'` emit `fiaf:SeparatedMagneticSound` when a perforated film gauge (`ba:Filmbreite` other than `'6,25_mm'` / `'Unbekannt'`) is present, and `fiaf:AudioElement` otherwise.
  - Note for NB (`5.6`): apply the same coordination when `carrier_type_specific = 'Sepmag'` is paired with `gauge = '35mm'` or `'16mm'`.
- **Affected Files** *(all updated)*:
  - `transform/bundesarchiv/xsl/bundesarchiv.xsl`

---

### 2.4 Sound Followers (`SoundNegative`, `SoundPositive`, `SeparatedMagneticSound`) vs. `AudioMaster` and Polarity
- **Status**: **OPEN**
- **Issue**:
  - In the current `fiaf:Element` hierarchy, `SoundNegative`, `SoundPositive`, `SeparatedMagneticSound`, and `AudioMaster` are all flat siblings under `fiaf:AudioElement`.
  - Two questions arise:
    1. In BFI (`BFI_FIAF_LOD_Items.xsl` line 1132), `'Master Magnetic Recording'` maps to `fiaf:AudioMaster`, whereas `'Magnetic recording'` and `'Dupe Magnetic Recording'` map to `fiaf:SeparatedMagneticSound`. Should `'Master Magnetic Recording'` emit both `fiaf:SeparatedMagneticSound` and `fiaf:AudioMaster`, or only one?
    2. In `BFI_FIAF_LOD_Items.xsl` line 929, `'Re-recorded Internegative'` is mapped to `fiaf:SoundNegative` (and triggers `OpticalSoundProcess` at line 201), whereas the original unified-taxonomy plan placed it under `fiaf:DuplicateNegative`. Which is right for BFI?
- **Resolution**: *Pending discussion.*

---

### 2.5 Generic `'Positive'` Mapped to `fiaf:ReleasePrint` Instead of `fiaf:Positive` in BFI Items
- **Status**: **OPEN**
- **Issue**:
  - `fiafcore-element.ttl` now defines both `fiaf:Positive` ("A positive film Element of unspecified generation") and its subclass `fiaf:ReleasePrint` ("A positive print made for exhibition, distribution, or viewing access").
  - In `BFI_FIAF_LOD_Items.xsl`, all generic positive descriptions (`'Positive'`, `'BW Positive'`, `'Colour Positive'`, `'Original Positive'`, `'Original / Dupe Positive'`, `'Tinted Positive'`, etc.) are mapped to `fiaf:ReleasePrint` instead of `fiaf:Positive`.
  - When combined with `copy_status = 'Master'` (`fiaf:hasStatus fiaf:Preservation`), this asserts that BFI master positives and original positives are theatrical `ReleasePrint`s.
  - Note: in `bundesarchiv.xsl`, `'Stummes_Positiv'` and `'Bildpositiv'` map to `fiaf:Positive`, while `'Kombinierte_Kopie'` and `'Stumme_Kopie'` map to `fiaf:ReleasePrint`.
- **Questions to Resolve**:
  - Should unspecified BFI positives (`'Positive'`, `'BW Positive'`, `'Colour Positive'`, `'Original Positive'`, `'Original / Dupe Positive'`, `'Tinted Positive'`, etc.) map to `fiaf:Positive` (or check `copy_status = 'Viewing'` vs `'Master'`), reserving `fiaf:ReleasePrint` for known prints/viewing copies?
- **Resolution**: *Pending discussion.*

---

### 2.6 Missing `hasFormat` Mappings in `bundesarchiv.xsl` for Video/Digital `Materialart` Values
- **Status**: **OPEN**
- **Issue**:
  - In `bundesarchiv.xsl`, the `isElement` block (lines 2713–2955) ignores several `Materialart` values because they represent formats, but the `hasFormat` block (lines 2112–2242) omits them:
    - `High_8/8mm` → could map to `fiaf:Video8` (parent of `fiaf:Hi8`)
    - `D_1_oder_2` → `fiaf:VideoFormat`
    - `BETA` → `fiaf:VideoFormat` (ambiguous between Betacam and Betamax)
    - `MAZ` (*Magnetaufzeichnung*, generic videotape) → `fiaf:VideoFormat`
    - `AMPEX_DCT`, `XDCAM_PFD_50DLA` → `fiaf:VideoFormat` / `fiaf:OpticalVideoDisc`
    - `FILE` → `fiaf:DigitalFormat` (when no more specific `ba:Container` is present)
- **Resolution**: *Pending discussion.*

---

### 2.7 `Positive` / `Negative` / `SeparatedMagneticSound` Stay in `Element` (Not `Format`)
- **Status**: **RESOLVED (design decision)**
- **Issue**:
  - `fiaf:Positive`, `fiaf:Negative`, and the magnetic-sound element classes look at first glance like *technology* rather than *function*, suggesting they should move from `fiaf:Element` to `fiaf:Format`, leaving `fiaf:Element` for media-agnostic workflow roles (Original, Intermediate/Duplicate, Master, Access/Release).
  - The concern was that `fiaf:Element` duplicates the other taxonomies:
    - `fiaf:Format` already records magnetic gauge (`fiaf:16mmMagneticFilm`, `fiaf:35mmMagneticFilm`) and audio carriers (`fiaf:QuerterInchAudiotape`, `fiaf:Audiocassette`, `fiaf:DAT`, …).
    - `fiaf:SoundStandard` already records the magnetic recording process (`fiaf:Magnetic` → `fiaf:FourTrackMagnetic`, `fiaf:SixTrackMagnetic`).
    - `fiaf:SeparatedMagneticSound` therefore appeared redundant with both.
- **Resolution (keep polarity and magnetic sound in `fiaf:Element`)**:
  1. **Photochemical function and polarity are structurally inseparable**. Duplication inverts polarity at every generation, so an element's role in the chain *is* its polarity:
     - **Camera capture** → `fiaf:OriginalNegative`: exists to be printed from, never projected.
     - **Protection / duplication master** → `fiaf:DuplicatePositive` (interpositive, fine-grain master) and `fiaf:ColourSeparationPositive`: must be positive *because* they are struck from the original negative and are printed onto negative stock.
     - **Printing master** → `fiaf:DuplicateNegative` (internegative) and `fiaf:ColourReversalIntermediate`: must be negative *because* release prints are struck from them onto positive print stock at high speed, protecting the original.
     - **Editorial / grading / exhibition** → `fiaf:WorkPrint`, `fiaf:AnswerPrint`, `fiaf:ReleasePrint`: must be positive because a human eye or projector must see a normal image.
     - The decisive case is the duplication intermediate: an interpositive and an internegative share the *same function* and differ *only* by polarity. `fiaf:ReversalPositive` is likewise an *original* (camera capture) that is nonetheless a positive. Polarity therefore cannot be factored out of `Element`.
  2. **Separate sound elements follow the same logic**. `fiaf:SoundNegative` exists to be married with the picture negative to print a combined `fiaf:ReleasePrint` (or to strike a `fiaf:SoundPositive`); a `fiaf:SoundPositive` can be played back directly or used to strike a `fiaf:SoundNegative`. `fiaf:SeparatedMagneticSound` (sepmag) is the non-inverting magnetic counterpart of that same separate-sound follower/master role.
  3. **The four layers are complementary, not redundant**:
     - `fiaf:hasFormat fiaf:35mmMagneticFilm` states the physical gauge/material (perforated magnetic film).
     - `fiaf:hasSoundStandard fiaf:Magnetic` (or `fiaf:FourTrackMagnetic`) states the recording process and track layout.
     - `fiaf:hasNoiseReduction fiaf:DolbyA` (or `fiaf:DolbySR`) states the companding system applied to that recording, where known.
     - `fiaf:isElement fiaf:SeparatedMagneticSound` states the element's *role*: a sound-only element carried separately from the image, as distinct from `fiaf:AudioMaster` (a master audio recording), `fiaf:SoundNegative`, and `fiaf:SoundPositive`.
     - Collapsing these would lose the distinction between a sepmag sound follower, an optical sound negative, and a magnetic audio master that happen to share a gauge or a recording process.
  4. **`Positive` / `Negative` are required fallback levels for real catalogue data**. Archives frequently record polarity without generation — Bundesarchiv `Bildnegativ`, `Bildpositiv`, `Stummes_Positiv`; BFI `Original / Dupe Negative`, `TV (low contrast) Positive`, `Reversal Colour Negative`. Without `fiaf:Negative` and `fiaf:Positive` as intermediate classes under `fiaf:FilmElement`, `fiaf:isElement` would have to guess a generation or drop the statement.
  5. **Moving polarity into `fiaf:Format` would break that property's role**. `fiaf:hasFormat` also has domain `fiaf:Manifestation`, where the polarity of a specific artefact is meaningless. Placing `Positive`/`Negative` under `fiaf:FilmFormat` would mix gauge with emulsion polarity in one branch (`35mmFilm` and `PositiveFilm` as peers), forcing two `hasFormat` statements for a single physical characteristic and inviting a `35mmPositiveFilm` cross-product.
  - **Accepted drawback**: `fiaf:Element` is *not* purely functional. It is "functional role, including film polarity where polarity is part of the role". `AudioElement`, `VideoElement`, and `DigitalElement` carry no polarity, which is correct — polarity is a photochemical concept and only `FilmElement` is organised by it.
  - This decision does **not** settle the mapping questions in **§2.4** (whether `'Master Magnetic Recording'` should also be an `fiaf:AudioMaster`, and whether BFI `'Re-recorded Internegative'` is `fiaf:SoundNegative` or `fiaf:DuplicateNegative`). Those remain open within the retained hierarchy.
- **Affected Files**:
  - `TAXONOMY_OVERVIEW.md` (Core Design Principle 3, §2.2 Element)
  - No ontology changes: `ontology/fiafcore-element.ttl`, `ontology/fiafcore-format.ttl`, and `ontology/fiafcore-soundstandard.ttl` already reflect this decision after `element-taxonomy`, `restructure-format-taxonomy`, and `restructure-sound-taxonomy` were merged.

---

## Part 3: Sound Taxonomy & Mappings

### 3.1 `Silent` vs. `Mute` on Sound-Era Intermediates and Masked Prints (`bundesarchiv.xsl`)
- **Status**: **OPEN**
- **Issue**:
  - In `bundesarchiv.xsl` (lines 2576–2601), any `Materialart` starting with `Stumm...` is mapped to `fiaf:Silent`:
    - `Stumme_Kopie_mit_Tonkasch`, `Stummes_Duplikatnegativ_mit_Tonkasch`, `Stummes_Internegativ_mit_Tonkasch`, `Stummes_Duplikatpositiv_mit_Tonkasch` ("with soundtrack mask")
    - `Stummes_Internegativ`, `Stummes_Intermediate_Negative`, `Stummes_Intermediate_Positve`, `Stummes_Color_Reversal_Intermediate`
  - Meanwhile, line 2603 maps `Kopie_mit_Tonkasch` to `fiaf:Mute`.
  - In FIAF cataloguing, a silent-era film (or print intended for silent exhibition) is `fiaf:Silent`, whereas an image-only intermediate element (`Internegativ`, `CRI`, `Intermediate`) or an element with a reserved soundtrack mask (`mit Tonkasch`) is `fiaf:Mute` (or in German archive usage, *stumm* is used indiscriminately for both `Silent` and `Mute` image-only elements).
- **Questions to Resolve**:
  - Should `..._mit_Tonkasch` and modern colour intermediates (`Stummes_Internegativ`, `Stummes_Intermediate_Negative`, `Stummes_Intermediate_Positve`, `Stummes_Color_Reversal_Intermediate`) in `bundesarchiv.xsl` map to `fiaf:Mute` instead of `fiaf:Silent`?
- **Resolution**: *Pending discussion.*

---

### 3.2 `fiaf:Stereo` vs. `fiaf:Surround` Disjointness (`Surround Stereo` in BFI)
- **Status**: **OPEN**
- **Issue**:
  - `ontology/fiafcore-soundchannelconfiguration.ttl` defines:
    - `fiaf:Stereo`: *"Stereophonic sound reproduced through two or more directional front channels **without surround channels**."*
    - `fiaf:Surround`: *"Multi-channel sound incorporating one or more surround channels in addition to screen channels."*
  - In `BFI_FIAF_LOD_Manifestations.xsl` (lines 795–797), `$sound_standard = 'Surround Stereo'` emits **both** `fiaf:Stereo` and `fiaf:Surround` on the same `SoundCharacteristic` blank node, which is a contradiction under those definitions.
- **Questions to Resolve**:
  - Should `'Surround Stereo'` in `BFI_FIAF_LOD_Manifestations.xsl` map only to `fiaf:Surround`, or should the definition of `fiaf:Stereo` be adjusted?
- **Resolution**: *Pending discussion.*

---

### 3.3 Homogeneous Sound Trees: `SoundStandard` vs. `NoiseReduction`, `SDDS`, and Multi-Track Carriers
- **Status**: **RESOLVED**
- **Issue**:
  - `SoundStandard` mixed orthogonal facets in one tree: the physical/encoding process or system (`OpticalSoundProcess`, `Magnetic`, `DigitalSoundSystem`), and analogue noise reduction (`NoiseReduction` → `Dolby`, `DolbyA`, `DolbySR`). Values such as BFI `'Dolby Stereo SR'` (`DolbyStereo` + `DolbySR`) and `TAXONOMY_OVERVIEW.md` Example 4 (`FourTrackMagnetic` + `DolbyA`) therefore mixed two different kinds of statement on one node.
  - `SDDS` sat under `OpticalSoundProcess` while its digital peers `DolbyDigital` and `DTS` sat under `DigitalSoundSystem`, even though all three are digital systems that may be carried optically on 35mm film.
  - A single carrier can hold several soundtracks (e.g. a 35mm quad-track print with SDDS, Dolby Digital, a Dolby Stereo SR analogue variable-area track, and DTS timecode), but the mapping had no rule for keeping each track's attributes separate.
- **Resolution**:
  - Added `ontology/fiafcore-noisereduction.ttl` with a homogeneous `NoiseReduction` tree: `Dolby` (unspecified), `DolbyA` and `DolbySR` as subclasses of `Dolby`.
  - Added `fiaf:hasNoiseReduction` (domain `SoundCharacteristic`, range `NoiseReduction`).
  - Removed `NoiseReduction`, `Dolby`, `DolbyA`, and `DolbySR` from `SoundStandard`; kept all IRIs unchanged.
  - Moved `SDDS` from `OpticalSoundProcess` to `DigitalSoundSystem`, alongside `DolbyDigital` and `DTS`. `DolbyStereo` and `UltraStereo` remain under `OpticalVariableArea`.
  - Adopted **one `SoundCharacteristic` node per soundtrack** on a carrier. A quad-track 35mm print therefore carries four nodes; noise reduction and channel layout attach to the correct track.
  - Updated BFI mappings: `'Dolby'` and `'Dolby SR'` now emit `hasNoiseReduction`; `'Dolby Stereo SR'` emits `hasSoundStandard fiaf:DolbyStereo` + `hasNoiseReduction fiaf:DolbySR`; `'DTS Sound (Optical)'` emits only `hasSoundStandard fiaf:DTS` (an analogue optical backup track, if present, is its own node).
- **Rationale**:
  - **Homogeneity rule**: each tree answers one question. `SoundStandard` answers "how is this soundtrack fixed or encoded?", `NoiseReduction` answers "what companding is applied?", and `SoundChannelConfiguration` answers "what is the channel layout?".
  - **Why split only noise reduction**: noise reduction is genuinely orthogonal — the same variable-area or magnetic track can use Dolby A, Dolby SR, or none. A full `SoundProcess` / `SoundSystem` split was rejected because analogue systems are specialisations of their fixation process (`DolbyStereo` *is* variable-area optical; `FourTrackMagnetic` *is* magnetic), and splitting would lose that inference or force duplicate statements. Digital systems are carried by film, disc, or file, and the carrier is already stated by `hasFormat`.
  - **Why `SDDS` moved**: `SDDS`, `DolbyDigital` and `DTS` are all digital systems; their optical printing is a carrier detail, not an analogue optical sound process. Keeping `SDDS` under `OpticalSoundProcess` split the three peers and made `DigitalSoundSystem` queries incomplete.
  - **Why one node per soundtrack**: a 35mm quad-track print needs `DolbySR` and `Stereo` bound to the analogue track, not to the SDDS or DTS track. The `SoundCharacteristic` node is the grouping device, exactly as `ColourCharacteristic` groups encoding/space/transfer.
  - **Why `DolbyA` / `DolbySR` under `Dolby`**: `Dolby` is the "specific type unknown" level; the subclasses add precision without losing broad `Dolby` queries.
  - **Trade-off**: `DolbyStereo` remains an `OpticalVariableArea` while `SDDS` is a `DigitalSoundSystem`, so values in `SoundStandard` can sit at different levels of specificity. This is intentional; `SoundStandard` is a specificity hierarchy, not a set of orthogonal facets. Cardinality and disjointness are not yet enforced in OWL.
- **Affected Files** *(all updated)*:
  - `ontology/fiafcore-soundstandard.ttl`, `ontology/fiafcore-noisereduction.ttl` (new), `ontology/fiafcore-soundcharacteristic.ttl`
  - `vocabulary/fiafcore-soundstandard.ttl`, `vocabulary/fiafcore-noisereduction.ttl` (new) & `fiafcore.ttl` (regenerated)
  - `compile.py` (vocabulary list)
  - `SOUND_TAXONOMY.md`, `TAXONOMY_OVERVIEW.md` (Principle 2/3, §2.4, Examples 2, 4, 7), `MAPPING.md` (§6.11), `docs/templates/vocabularies.html`
  - `transform/bfi/xsl/BFI_FIAF_LOD_Manifestations.xsl`
- **Note**: §3.1 (`Silent` vs. `Mute`) and §3.2 (`Stereo` vs. `Surround`) remain separate open mapping questions.

---

## Part 4: Cross-Ontology Interactions & Bugs

### 4.1 Missing Label on `fiaf:Element` Root Class
- **Status**: **OPEN**
- **Issue**:
  - In `ontology/fiafcore-element.ttl` (lines 7–10), `<https://dev.fiafcore.org/Element>` has `rdfs:label ""@en` and `dc:description ""@en`.
  - This causes `vocabulary/fiafcore-element.ttl` to have an empty `skos:prefLabel ""@en` on the `ConceptScheme`.
- **Proposed Fix**:
  - Set `rdfs:label "Element"@en` and add a concise `dc:description` on `fiaf:Element`, then re-run `uv run compile.py`.
- **Resolution**: *Pending discussion.*

---

### 4.2 Domain of `fiaf:hasLanguageUsage` Excludes `fiaf:Item`
- **Status**: **OPEN**
- **Issue**:
  - In `ontology/fiafcore-work.ttl` (line 93), `fiaf:hasLanguageUsage` has `rdfs:domain [ owl:unionOf (Work Variant Manifestation) ]`.
  - However, `example/Item.ttl` (line 18), `bundesarchiv.xsl` (line 2273), and NB (`MAPPING.md` §4.3) all use `fiaf:hasLanguageUsage` on `fiaf:Item` (since individual prints/items can have different subtitle or dubbing languages).
- **Proposed Fix**:
  - Add `<https://dev.fiafcore.org/Item>` to the `owl:unionOf` domain of `fiaf:hasLanguageUsage` in `ontology/fiafcore-work.ttl`.
- **Resolution**: *Pending discussion.*

---

### 4.3 Domain of `fiaf:hasBroadcastStandard` Excludes `fiaf:Manifestation`
- **Status**: **OPEN**
- **Issue**:
  - In `ontology/fiafcore-item.ttl` (line 31), `fiaf:hasBroadcastStandard` has `rdfs:domain <https://dev.fiafcore.org/Item>` only.
  - Broadcast and home-viewing manifestations (`BroadcastManifestation`, `HomeViewingManifestation`) also have broadcast standards (e.g., BFI `BFI_FIAF_LOD_Manifestations.xsl` line 314 has `Phase Alternate Line (PAL)` on Manifestations, which had to be dropped).
- **Proposed Fix**:
  - Expand `rdfs:domain` of `fiaf:hasBroadcastStandard` to `[ owl:unionOf (Manifestation Item) ]` (matching `hasFormat`, `hasColourCharacteristic`, `hasSoundCharacteristic`, and `hasExtent`).
- **Resolution**: *Pending discussion.*

---

### 4.4 `owl:ObjectProperty` Typo on Datatype Properties in `fiafcore-event.ttl` & `fiafcore-identifier.ttl`
- **Status**: **OPEN**
- **Issue**:
  - Under `### Datatype Properties` in `ontology/fiafcore-event.ttl` (lines 297–335) and `ontology/fiafcore-identifier.ttl` (line 19), six properties with literal `xsd:*` ranges (`hasAchievement`, `hasAwardName`, `hasDate`, `nominationOnly`, `hasVerdict`, `hasIdentifierValue`) are declared as `a owl:ObjectProperty` instead of `a owl:DatatypeProperty`.
- **Proposed Fix**:
  - Change their `rdf:type` to `owl:DatatypeProperty`.
- **Resolution**: *Pending discussion.*

---

### 4.5 `fiaf:Stock` Instance vs. Class IRI Inconsistency & SKOS Vocabulary List
- **Status**: **OPEN**
- **Issue**:
  - `example/Item.ttl` (line 22), `BFI_FIAF_LOD_Items.xsl` (line 237), and NB (`MAPPING.md` §4.3) emit `fiaf:hasStock [ a fiaf:Kodak ; fiaf:hasStockCode "..." ]` (an instance of the `Stock` subclass, because `fiaf:hasStockCode` has `rdfs:domain fiaf:Stock`).
  - `bundesarchiv.xsl` (lines 2695–2701) emits `<fiaf:hasStock rdf:resource="https://dev.fiafcore.org/Kodak" />` directly (class IRI as value, rather than a blank node with `<rdf:type rdf:resource="..."/>`), and drops stock formulation codes like `DP_31`, `DN_21`, `PF2`, `ST_8`, `2374`, `2234`, `2366`, `CP_30`, `TF_12d` (lines 2682–2692) which are actually Orwo/Agfa/Kodak `hasStockCode` values!
- **Proposed Fix**:
  - Align `bundesarchiv.xsl` with BFI/NB/`example/Item.ttl` by emitting `<fiaf:hasStock><rdf:Description><rdf:type rdf:resource="..."/></rdf:Description></fiaf:hasStock>`, and optionally map the known Orwo/Kodak stock formulation codes (`DP_31`, `DN_21`, `PF2`, `2374`, etc.) using `fiaf:hasStockCode`.
- **Resolution**: *Pending discussion.*

---

### 4.6 Other XSLT & Documentation Bugs Noticed During Audit
- **Status**: **OPEN**
- **Issues**:
  1. `transform/bundesarchiv/xsl/bundesarchiv.xsl` line 198: `'Griechenland'` (Greece) is mapped to `fiaf:Greenland` instead of `fiaf:Greece`.
  2. `transform/bundesarchiv/xsl/bundesarchiv.xsl` lines 1775 and 2969: stray `-->` after `<xsl:template match="ba:Exemplar">` and `<xsl:template match="ba:Aufbewahrungseinheit">`.
  3. **Resolved**: `FORMAT_TAXONOMY.md` previously stated that `fiaf:RealVideo` and `fiaf:WindowsMedia` were removed, whereas `ontology/fiafcore-format.ttl` preserves them under `fiaf:VideoCodec`. The document now matches the ontology.
- **Resolution**: *Pending discussion for items 1–2; item 3 is resolved.*

---

### 4.7 Evaluating `Element` as `rdf:type` Subclasses of `fiaf:Item` ([GitHub Discussion #142](https://github.com/FIAF/fiafcore/discussions/142))
- **Status**: **OPEN (Future Architectural Review)**
- **Context**:
  - [Discussion #142](https://github.com/FIAF/fiafcore/discussions/142) raised the question of whether `fiaf:Format` and `fiaf:Element` should migrate to subclasses of `fiaf:Carrier` and `fiaf:Item`.
  - Turning `Format` into `rdf:type` subclasses of `Carrier` does **not** fit well: `Manifestation`s also carry `fiaf:hasFormat`; many archives (e.g. BFI) do not export `Carrier` records; and digital stream codecs (`FFV1`, `PCM`, `ProRes`) are encoding formats attached via `fiaf:hasFormat`, not subclasses of a carrier/unit (`<carrier> a fiaf:FFV1` fails the ontological "is-a" test). Expanding `fiaf:hasFormat` to domain `Manifestation ∪ Item ∪ Carrier` (resolved in **2.1**) solves carrier-level format description cleanly.
  - By contrast, **using `Element` as `rdf:type` subclasses of `fiaf:Item`** (while keeping `fiaf:hasFormat` as a property) has strong ontological and structural merits worth revisiting:
    1. **Ontological "is-a" fit**: Saying `<item> a fiaf:ReleasePrint`, `<item> a fiaf:OriginalNegative`, or `<item> a fiaf:DigitalMaster` is completely natural—an element type literally *is* a kind of `Item`. Even the existing property name `fiaf:isElement` (the only `isX` property in FIAFcore alongside `hasX` properties) reflects `rdf:type`.
    2. **Symmetry across all four WEMI levels**: `Work` (`MonographicWork`), `Variant` (`DubbedVariant`), and `Manifestation` (`TheatricalManifestation`) all express their primary classification via `rdf:type` subclasses; `Item` is currently the only WEMI class with `# None` under `### Subclasses`.
    3. **Multi-element items**: RDF/OWL allows multiple `rdf:type` assertions on an `Item` (just as on `Variant`), and unspecified items naturally fall back to `a fiaf:Item` (or `a fiaf:FilmElement`).
    4. **Eliminates OWL punning**: `Element` classes would be used directly as OWL classes (`rdf:type`) rather than as object values of `fiaf:isElement`.
- **Trade-offs & Questions to Decide When Revisiting**:
  1. **Querying without RDFS reasoning (e.g. QLever)**: Whether transforms should emit both `a fiaf:Item` and `a fiaf:ReleasePrint` (as NB already does for `Manifestation` + subtype), or rely on `rdf:type/rdfs:subClassOf* fiaf:Item`.
  2. **Hierarchy linkage & backwards compatibility**: Whether `fiaf:Element` becomes `rdfs:subClassOf fiaf:Item` (or `FilmElement`/`AudioElement`/`VideoElement`/`DigitalElement` become direct subclasses of `fiaf:Item`), and whether `fiaf:isElement` is deprecated in parallel.
  3. **SKOS vocabulary generation**: Whether `vocabulary/fiafcore-element.ttl` should continue to be generated as a SKOS `ConceptScheme` or merge into `fiafcore-item.ttl`.
- **Resolution**: *Parked for dedicated architectural discussion.*

---

### 4.8 Replacing `fiaf:Carrier` with Partitive `fiaf:Item`s (`hasPart` / `isPartOf`) and Work-Independent Storage Media (`CARRIER_AND_DIGITAL_MODELING.md`)
- **Status**: **OPEN (Future Architectural Review)**
- **Dependency from the Format/stream decision**: Carrier remains vaguely defined and is not settled by §4.10. `hasStream` provisionally accepts Item ∪ Carrier as equally valid attachment points; archives are not required to use any inventory entity below Item. The eventual entity review must distinguish storage units, digital objects, package components, and internal streams. Keep storage and digital-object formats on separate objects where possible; storage/content relationships must not be conflated with stream composition. No hasContent/isContentOf or package-part relation is introduced by the stream change.
- **Context**:
  - **Lineage & Standards Alignment**:
    - The FIAF Moving Image Cataloguing Manual (2016) defines **four core entities** (`Work`, `Variant`, `Manifestation`, `Item`); `Carrier` is not a primary entity in the FIAF Manual and has no `dc:source` citation in `ontology/fiafcore-carrier.ttl`.
    - Both **RDA** ([`rdai:P40009`](https://www.rdaregistry.info/Elements/i/#P40009) *"is contained in item"* / [`rdai:P40034`](https://www.rdaregistry.info/Elements/i/#P40034) *"is container of item"*, plus sibling properties `rdai:P40029` *"is held with"* and `rdai:P40032` *"is bound with"*) and **EBUCore** (`ebucore:MediaResource` with `ebucore:hasPart` / `ebucore:isPartOf`) model discrete components (reels, cassettes, track files) and containers as recursive `Item`-to-`Item` whole–part relationships rather than a separate `Carrier` class.
  - **Reel- & Component-Level Property Gap on `fiaf:Carrier`**:
    - Currently, `fiaf:Carrier` can only take `hasIdentifier`, `hasEvent`, and `hasFormat`. It cannot carry `hasBase`, `hasStock`, `hasExtent`, `hasColourCharacteristic`, `hasSoundCharacteristic`, `hasStatus`, `isElement`, or `hasHoldingInstitution`.
    - In archival collections, material characteristics frequently vary at the reel or component-file level:
      - *Composite/spliced film items*: Reels 1–3 on `NitrateBase` (`Agfa`, `Tinted`) and Reel 4 on `AcetateBase` (`Kodak`, `BlackAndWhite`).
      - *Reel-by-reel extent & picture/sound pairs*: Individual reel lengths (`Foot`, `Metre`) or a picture reel (`35mmFilm`, `OriginalNegative`) paired with a separate sound reel (`35mmMagneticFilm`, `SeparatedMagneticSound`).
      - *Multi-file digital packages (`DCP`, `IMF`, `DPX`)*: A parent `DCP` `Item` (`hasFormat fiaf:DCP`) with child track `Item`s for picture (`MXF`, `XYZ`/`DCIP3`) and sound (`MXF`, `PCM`, `Surround`).
  - **Untangling `DigitalFormat` vs. `DataStorageFormat` (Many-to-One & One-to-Many Storage Media)**:
    - An offline storage carrier like an **LTO tape** (`fiaf:LTO6`) or **hard drive** (`fiaf:HardDrive`) is often **not** an embodiment of a single `Work`/`Manifestation`: one LTO tape in the vault may hold digital file `Item`s belonging to **20 different Works** (many-to-one), or a single 4K `DPX` scan may span **multiple LTO tapes** (one-to-many). Analogously, a compilation film reel can hold spliced prints of multiple short film `Work`s.
    - Modeling the digital file as a `fiaf:Item` (under its `Manifestation`, carrying `DigitalFormat` + `DigitalElement`) that links via `isPartOf` / `isContainedInItem` (or `hasCarrier`) to a **Work-independent storage carrier** (carrying `DataStorageFormat`, vault barcode `hasIdentifier`, `hasHoldingInstitution`, and storage `hasEvent`) cleanly separates the digital object from the physical storage medium.
  - **Counterpoint 1: Collection Quantification & Double-Counting (`Item` vs. `Carrier`)**:
    - Merging the logical copy (`Item`) and the physical shelf unit (`Carrier`) into a single `fiaf:Item` class breaks straightforward collection quantification in SPARQL:
      - *"How many copies/elements of Works do we hold?"* (`?x a fiaf:Item`) vs. *"How many film reels / cassettes / LTO tapes do we have on the shelves?"* (`?x a fiaf:Carrier`).
      - If a 5-reel print is modeled as 1 parent `Item` + 5 child `Item`s, `COUNT(?x a fiaf:Item)` returns **6** (neither 1 copy nor 5 reels).
      - Queries would have to rely on `FILTER NOT EXISTS { ?item fiaf:isPartOf ?parent }` or `FILTER NOT EXISTS { ?item fiaf:hasPart ?child }`, which is slow on large graphs and breaks down when hierarchy direction inverts between **multi-reel prints** (1 copy `Item` *hasPart* 5 reel `Item`s) and **shared LTO tapes / compilation reels** (1 LTO `Item` *hasPart* 20 file `Item`s).
  - **Counterpoint 2: The Single-Reel / Single-Unit Wrapper Problem (`1 Item` + `1 ITEM_PART`)**:
    - Conversely, strictly separating `Item` and `Carrier` in cataloguing systems (such as NB's `ITEM` → `ITEM_PART`) currently forces cataloguers to create **1 `Item` with 1 child `ITEM_PART` (`Carrier`)** for every single-reel film, single videocassette, or single digital file just so `Carrier` counts stay complete—an unnecessary wrapper layer that adds friction and duplicates metadata.
    - **How to avoid the 1:1 wrapper while preserving exact `Item` and `Carrier` counts**:
      - **Dual-typing single-unit holdings (`a fiaf:Item, fiaf:Carrier`)**: When a holding consists of a single physical/digital unit placed directly under `Manifestation` in the catalog, emit a **single node** typed as **both** `a fiaf:Item, fiaf:Carrier` (whereas a 5-reel print has 1 parent `a fiaf:Item` and 5 children `a fiaf:Carrier`). Then `COUNT(?i a fiaf:Item)` counts copies (1 + 1 = 2) and `COUNT(?c a fiaf:Carrier)` counts shelf units (1 + 5 = 6) with zero redundant wrapper nodes and zero `FILTER NOT EXISTS` clauses.
      - **Or allow `fiaf:hasCarrier` directly on `Manifestation`** (domain `Manifestation ∪ Item`) for single-unit holdings when no separate `Item` grouping layer is needed.
- **Architectural Options & Questions to Decide When Revisiting**:
  1. **Option A (Replace `Carrier` with Partitive `Item`s)** vs. **Option B (Retain & Enrich `fiaf:Carrier`)**:
     - Under **Option B**, keep `fiaf:Carrier` distinct from `fiaf:Item`, expand reel-variable property domains (`hasBase`, `hasStock`, `hasExtent`, `hasColourCharacteristic`, `hasSoundCharacteristic`) to include `Carrier`, allow many-to-one `Item ──hasCarrier──► Carrier` for shared LTO tapes and compilation reels, and support single-unit holdings directly under `Manifestation` (via `a fiaf:Item, fiaf:Carrier` dual-typing or `Manifestation ──hasCarrier──► Carrier`).
  2. **Typing of Work-Independent Storage Containers (under Option A)**: If `Carrier` were removed, should a shared LTO tape or hard drive be typed as a `fiaf:Item` or a dedicated `fiaf:StorageCarrier` class?
  3. **Property Naming & Domain (under Option A)**: RDA-aligned Item-specific properties (`fiaf:isContainedInItem` / `fiaf:containsItem`) vs. general whole–part properties (`fiaf:hasPart` / `fiaf:isPartOf`).
  4. **Ordering / Sequence of Parts**: How should Reel 1, Reel 2, Reel 3 be ordered when needed (e.g. `rdfs:label`, `Identifier`, or a lightweight `fiaf:hasPartNumber` datatype property)?
  5. **Migration Impact**: How should `example/Carrier.ttl`, `bundesarchiv.xsl` (`ba:Aufbewahrungseinheit`), and NB (`ITEM` / `ITEM_PART`) align with the chosen option?
- **Resolution**: *Parked for dedicated architectural discussion (see `CARRIER_AND_DIGITAL_MODELING.md` for full analysis and Turtle examples).*

---

### 4.9 Homogeneous vs. Heterogeneous Taxonomy Trees: One Kind of Thing per Tree (Colour, Sound, Format, and Untouched Taxonomies)
- **Status**: **PARTIALLY RESOLVED (Sound resolved; Format and the untested trees remain open)**
- **Issue**:
  - The technical taxonomies do not agree on **what a second value from the same tree means**. In some trees every concept is an instance of the *same kind of thing*, so repeating the property means "more than one of these is present". In others the tree bundles *several different kinds of things* (orthogonal facets), so repeating the property means "this artefact has several different dimensions". That is a **semantic homogeneity** problem, not a cardinality problem:
    - **Homogeneous trees (one kind of thing)**:
      - `ColourStandard`: every concept answers "which colour process is present?". `fiaf:Tinted` + `fiaf:Toned` is therefore not a contradiction; it states that **both processes are present** (e.g. a print that is both tinted and toned). The tree is not strictly "mutually exclusive" — exclusivity only applies to specific values that cannot physically co-occur.
      - `ColourEncoding` (`RGB`, `YUV`, `XYZ`, `Greyscale`), `ColourSpace` (`Rec709`, `ACES2065_1`, …), and `TransferFunction` (`Linear`, `Gamma`, …): each tree covers one digital dimension. These aspects are separately describable, but not every combination is meaningful: ACES2065-1 specifies RGB encoding and a linear transfer function (`TAXONOMY_OVERVIEW.md`, Principles 1–2).
      - `SoundChannelConfiguration` (`Mono`, `Stereo`, `Surround`) and the `BlackAndWhite` / `Colour` and `Sound` / `Silent` / `Mute` type branches are homogeneous too.
      - The current documentation models hybrid colour as **separate blank nodes**, but that is a modelling choice for characteristics on different sequences, not a rule that a single node may hold only one `hasColourProcess`. `TAXONOMY_OVERVIEW.md` Example 3 uses `[ fiaf:hasColourProcess fiaf:Toned ], [ a fiaf:Colour ; fiaf:hasColourProcess fiaf:Technicolor ]` because those processes occur on different parts of the print; `Tinted` + `Toned` on the same part could legitimately sit on one node.
    - **Heterogeneous trees (several kinds of thing in one tree)**:
      - **`SoundStandard`** *(resolved — see Resolution below)* previously mixed three orthogonal facets under one property and one tree:
        1. **Physical fixation process**: `OpticalSoundProcess` (`OpticalVariableArea`, `OpticalVariableDensity`), `Magnetic` (`FourTrackMagnetic`, `SixTrackMagnetic`).
        2. **Playback / encoding system**: `DigitalSoundSystem` (`DolbyDigital`, `DTS`, `DolbyAtmos`, …), plus `DolbyStereo` and `SDDS` under `OpticalSoundProcess`.
        3. **Noise reduction**: `NoiseReduction` (`Dolby`, `DolbyA`, `DolbySR`).
        Stating `fiaf:DolbyStereo` + `fiaf:DolbySR` therefore said two **different kinds of things** about one track (a playback system and a noise-reduction system), not "two playback systems are present":
        - BFI `'Dolby Stereo SR'` → `fiaf:hasSoundStandard fiaf:DolbyStereo, fiaf:DolbySR` (`BFI_FIAF_LOD_Manifestations.xsl` lines 804–807).
        - BFI `'DTS Sound (Optical)'` → `fiaf:hasSoundStandard fiaf:DTS, fiaf:OpticalSoundProcess` (lines 784–787) mixed a digital encoding system with the physical carrier process.
        - `TAXONOMY_OVERVIEW.md` Example 4 → `fiaf:hasSoundStandard fiaf:FourTrackMagnetic, fiaf:DolbyA` (line 656) mixed a track layout with a noise-reduction system.
        - `fiaf:DolbyStereo` is itself a subclass of `fiaf:OpticalSoundProcess`, so some statements mixed a system with its own parent process at two levels of the same branch.
        - **Now**: `NoiseReduction` is its own tree (`fiafcore-noisereduction.ttl`) reached via `fiaf:hasNoiseReduction`; `DolbyA` and `DolbySR` are subclasses of `Dolby` (unspecified); `SDDS` moved under `DigitalSoundSystem`; and multi-track carriers use one `SoundCharacteristic` node per soundtrack.
      - **`Format`** mixes physical carriers, file wrappers/packages, and stream codecs under one property and one tree:
        - Physical carrier / gauge: `FilmFormat` (`35mmFilm`), `VideoFormat` (`DigitalBetacam`, `DVD`), `AudioFormat` (`CD`), `DataStorageFormat` (`LTO5`, `DVDR`).
        - Container / package / image file: `ContainerFormat` (`MKV`, `MXF`, `MP4`, `VOB`), `PackageFormat` (`DCP`, `IMF`), `ImageFormat` (`DPX`, `TIFF`).
        - Stream codec: `VideoCodec` (`FFV1`, `ProRes`), `AudioCodec` (`PCM`).
        A single `Item` or `Carrier` routinely carries several values, each of a different kind:
        - `fiaf:MKV` (`ContainerFormat`) + `fiaf:FFV1` (`VideoCodec`) + `fiaf:PCM` (`AudioCodec`) — `TAXONOMY_OVERVIEW.md` Example 6, lines 723–725.
        - `fiaf:DVD` (`OpticalVideoDisc`) + `fiaf:VOB` (`ContainerFormat`) — Example 5, lines 709–710.
        - `fiaf:DPX` (`ImageFormat`) + `fiaf:LTO5` (`DataStorageFormat`) — Principle 4 and §2.1.
        - `fiaf:MP4` (`ContainerFormat`) + `fiaf:DVDR` (`DataStorageFormat`) — Example 6, lines 762–763.
    - **`Element`** is currently single-valued by convention (`fiaf:isElement` once per `Item`), even where an artefact arguably occupies two roles (e.g. `SeparatedMagneticSound` + `AudioMaster`, §2.4). Nothing in the ontology enforces this either.
  - The practical consequence is that **the same shape encodes both valid repetition and facet mixing**, and nothing distinguishes them:
    - *Valid repetition or homogeneity violation*: `fiaf:hasSoundStandard fiaf:DolbyStereo, fiaf:DolbySR` previously meant "system + noise reduction"; it is now `fiaf:hasSoundStandard fiaf:DolbyStereo ; fiaf:hasNoiseReduction fiaf:DolbySR`.
    - *Facet mix*: `fiaf:hasFormat fiaf:MKV, fiaf:FFV1, fiaf:PCM, fiaf:LTO5` mixes container, video codec, audio codec, and storage medium.
    - *Genuine contradiction*: `fiaf:hasFormat fiaf:35mmFilm, fiaf:16mmFilm`, or `fiaf:hasSoundStandard fiaf:OpticalVariableArea, fiaf:OpticalVariableDensity`.
  - `SoundChannelConfiguration` is homogeneous, but the BFI `'Surround Stereo'` mapping still emits both `fiaf:Stereo` and `fiaf:Surround` on one node (§3.2), and the `Sound` / `Silent` / `Mute` values are `rdf:type` assertions rather than properties. These show that the intended semantics are implicit and therefore easy to break in new mappings.
- **Why It Matters**:
  - **Validation**: the problem is not maximum cardinality; it is **which combinations are compatible**. Homogeneous trees need `owl:AllDisjointClasses`/SHACL only for values that cannot co-occur, while heterogeneous trees need either separate properties or documented facet rules. Without that, contradictory and facet-mixing statements pass silently.
  - **Querying**: consumers cannot tell whether two `hasFormat` values mean "two systems present" or "a system plus its noise reduction", nor whether two `hasFormat` values are alternatives or complementary facets. For sound, `hasSoundStandard` (process/system) and `hasNoiseReduction` (companding) are now separate, so this ambiguity is resolved for sound; it remains for `hasFormat`.
  - **SKOS/vocabulary consumers**: `vocabulary/*.ttl` publishes every tree as a flat `skos:ConceptScheme`. Downstream users cannot see which branches are facets and which are alternatives.
  - **Mapping consistency**: BFI, Bundesarchiv, and NB each make ad-hoc choices about when to emit one value, several values, or several blank nodes. Without a stated rule, new mappings will keep diverging.
  - **Expansion risk**: §5.1 and §5.2 will add new `Form`, `Genre`, and `LanguageUsage` concepts. If those trees already mix facets, the additions will make the problem worse.
- **Taxonomies Still to Audit**:
  - The following trees have not yet been reviewed through this lens and should be checked before their planned expansions:
    1. **`fiaf:Form`** (`fiafcore-form.ttl`): mixes **length** (`FeatureFilm`, `ShortFilm`), **publication/structural mode** (`Serial`, `Series`, `CompilationFilm`), **production context** (`AmateurFilm`, `HomeMovie`), and **production-material purpose** (`Trailer`, `Outtake`, `ScreenTest`). It also overlaps the `Work` subclasses (`MonographicWork`, `SerialWork`, `CollectionWork`). Stating `fiaf:ShortFilm` + `fiaf:AmateurFilm` (or `fiaf:FeatureFilm` + `fiaf:CompilationFilm`) asserts different kinds of things.
    2. **`fiaf:Genre`** (`fiafcore-genre.ttl`): mixes **narrative/thematic genre** (`WesternFilm`, `HorrorFilm`, `ComedyFilm`, `MelodramaFilm`, `CrimeFilm`, `ScienceFictionFilm`), **technique/medium** (`AnimationFilm`, `PuppetFilm`, `HandPuppetFilm`, `StickPuppetFilm`, `MixedFilm`), **movement/style** (`ExpressionistFilm`, `SurrealistFilm`, `AbstractFilm`, `AvantGardeFilm`, `ExperimentalFilm`), **purpose/context** (`EducationalFilm`, `PropagandaFilm`, `ElectionFilm`, `IndustrialFilm`, `ResearchFilm`), **audience** (`ChildrensFilm`, `YouthFilm`, `WomensFilm`), and **adaptation status** (`LiteraryAdaptationFilm`). Multiple genres can legitimately co-occur (a comedy western), so the question is which axes may combine and whether technique/audience/purpose belong in `Genre` at all.
    3. **`fiaf:LanguageUsage`** (`fiafcore-languageusage.ttl`): mixes **modality** (`SpokenLanguage`, `SungLanguage`, `SignedLanguage`), **written placement** (`Subtitles`, `Intertitles`, `Captions`, `Credits`), and **absence** (`NoDialogue`, currently a subclass of `Dialogue`). §5.2 proposes adding original vs. dubbed and audio description/commentary, which would add **translation status** and **accessibility function** to the same tree.
    4. **`fiaf:Variant`** (`fiafcore-variant.ttl`): mixes **editorial change** (`CensoredVariant`, `CondensedVariant`, `AugmentedVariant`), **language/sound adaptation** (`DubbedVariant`, `SubtitledVariant`, `SonorizedVariant`), **colour modification** (`ColourizedVariant`, `GreyscaledVariant`), and **archival outcome** (`PreservationVariant`, `RestorationVariant`). Some combinations are legitimate (a dubbed and censored variant), but the axes differ.
    5. **`fiaf:Extent`** (`fiafcore-extent.ttl`): mixes **length units** (`Foot`, `Metre`), **duration units** (`Minute`, `Second`), **file-size units** (`Kilobyte`–`Terabyte`), and **carrier count** (`Reel`). Because each extent is normally a separate blank node, this is less immediately harmful, but `Extent` is still not one kind of thing.
  - **Trees that look homogeneous but should be verified**: `Base` (nitrate/acetate/polyester), `BroadcastStandard` (NTSC/PAL/SECAM), `Status` (Access/Preservation), `Title` (preferred/alternative/identifying/…), `Event` (lifecycle event types), `Activity`, `Agent`, `Identifier`, `Stock`, `Country`, `Language`, and `SoundChannelConfiguration`. For each, ask whether multiple values mean "more than one instance of the same kind" or "different facets of one artefact".
- **Questions to Resolve**:
  1. Which trees are **homogeneous** (one kind of thing, multiple values = several instances present) and which are **heterogeneous** (several facets, multiple values = different dimensions)?
  2. For heterogeneous trees, should each facet get its **own property and tree** (as Colour did with encoding/space/transfer, and as Sound now does with noise reduction), or should one property keep documented facet branches?
  3. Should the ontology enforce only **genuine incompatibilities** (`owl:AllDisjointClasses`, SHACL), rather than a blanket `maxCardinality 1`? Which values in homogeneous trees can never co-occur?
  4. ~~If Sound is split, what happens to existing classes and IRIs?~~ **Resolved**: `fiaf:SoundStandard` is retained as the process/system tree (IRIs unchanged), `NoiseReduction` becomes a sibling tree in `ontology/fiafcore-noisereduction.ttl` reached via `fiaf:hasNoiseReduction`, `DolbyA`/`DolbySR` become subclasses of `Dolby`, and `SDDS` moves under `DigitalSoundSystem`. `SoundProcess`/`SoundSystem` were not introduced, so existing `hasSoundStandard` consumers keep working.
  5. Should `fiaf:Tinted` + `fiaf:Toned` be allowed on one `ColourCharacteristic` node (two instances of the same kind), and should `TAXONOMY_OVERVIEW.md` Example 3 distinguish "same sequence" from "different sequences" explicitly?
  6. How should `fiaf:Format` distinguish **alternatives** (film gauge: `35mmFilm` vs. `16mmFilm`) from **complementary facets** (container + video codec + audio codec + storage medium)? Should stream codecs move to a technical-characteristic node instead (§5.5)?
  7. What is the facet analysis for `Form`, `Genre`, `LanguageUsage`, `Variant`, and `Extent`, and should it happen before or alongside §5.1/§5.2?
- **Options**:
  - **Option A — Split heterogeneous trees into homogeneous trees and properties (Colour-style)**:
    - Sound *(applied)*: `SoundStandard` retained for the fixation process / playback system; `NoiseReduction` (`Dolby` → `DolbyA`, `DolbySR`) split into its own tree and property `hasNoiseReduction`; `SDDS` moved under `DigitalSoundSystem`. A separate `SoundProcess`/`SoundSystem` pair was not introduced, because analogue systems are specialisations of their fixation process and multi-track carriers use one `SoundCharacteristic` node per soundtrack.
    - Format: keep `hasFormat` for physical carriers and packages, and add facet properties (e.g. `hasContainerFormat`, `hasVideoCodec`, `hasAudioCodec`) or move stream codecs to `TechnicalCharacteristic` (§5.5).
    - Apply the same analysis to `Form`, `Genre`, `LanguageUsage`, `Variant`, and `Extent`.
    - *Advantage*: every property has one meaning; repeated values always mean "more than one instance of the same kind"; contradictions become structurally impossible.
    - *Drawback*: more properties and more splits; breaking change for existing `hasSoundStandard`/`hasFormat` consumers; some concepts (e.g. `DolbyStereo`) straddle facets, so the split is not perfectly clean.
  - **Option B — Keep unified trees, declare facet branches and disjointness**:
    - Keep `hasSoundStandard`, `hasFormat`, and the other trees multi-valued, but document each top-level branch as a facet, state which branches may co-occur, and add `owl:AllDisjointClasses`/SHACL constraints for values that cannot co-occur (e.g. `OpticalVariableArea` vs. `OpticalVariableDensity`, `35mmFilm` vs. `16mmFilm`).
    - *Advantage*: no IRIs or properties removed; matches how archives describe combined tracks and multi-file digital objects.
    - *Drawback*: semantics remain conventional; validation needs shapes rather than plain OWL; SKOS consumers still see a flat scheme.
  - **Option C — Hybrid**: split only the facets that are already routinely multi-valued (`NoiseReduction`, digital container/codec/storage), while keeping umbrella trees for the rest and marking incompatible values as disjoint.
- **Affected Files** *(pending decision)*:
  - `ontology/fiafcore-colourcharacteristic.ttl`, `fiafcore-colourstandard.ttl`, `fiafcore-colourencoding.ttl`, `fiafcore-colourspace.ttl`, `fiafcore-transferfunction.ttl`
  - `ontology/fiafcore-soundcharacteristic.ttl`, `fiafcore-soundstandard.ttl`, `fiafcore-noisereduction.ttl`, `fiafcore-soundchannelconfiguration.ttl` *(sound split applied)*
  - `ontology/fiafcore-format.ttl`, `ontology/fiafcore-manifestation.ttl` (`fiaf:hasFormat`)
  - `ontology/fiafcore-form.ttl`, `fiafcore-genre.ttl`, `fiafcore-languageusage.ttl`, `fiafcore-variant.ttl`, `fiafcore-extent.ttl` (audit and possible splitting)
  - `TAXONOMY_OVERVIEW.md` (Core Design Principles 1–2, Examples 2–7), `SOUND_TAXONOMY.md` (§1, §4), `FORMAT_TAXONOMY.md` (§Notes), and §5.1/§5.2 of this review
  - `transform/bfi/xsl/BFI_FIAF_LOD_Manifestations.xsl` (lines 758–823), `transform/bundesarchiv/xsl/bundesarchiv.xsl` (lines 2577–2658)
  - `compile.py` and `vocabulary/*.ttl` if trees are split or added (the vocabulary list in `compile.py` is hardcoded)
- **Resolution**:
  - **Sound (resolved 2026-11-05)**: `NoiseReduction` is now an independent homogeneous tree in `ontology/fiafcore-noisereduction.ttl` (`Dolby` → `DolbyA`, `DolbySR`) reached through `fiaf:hasNoiseReduction`. `SoundStandard` keeps the fixation-process/playback-system tree, with `SDDS` moved under `DigitalSoundSystem` alongside `DolbyDigital` and `DTS`. Each `SoundCharacteristic` node describes exactly one soundtrack, so a multi-soundtrack carrier (e.g. a 35mm quad-track print) uses one node per track. BFI `'Dolby Stereo SR'` now emits `hasSoundStandard fiaf:DolbyStereo` + `hasNoiseReduction fiaf:DolbySR`, and `'DTS Sound (Optical)'` emits only `hasSoundStandard fiaf:DTS`. See **§3.3** for the full rationale, including why `SoundProcess` / `SoundSystem` were not split out.
  - **Format (implemented, see §4.10)**: retain the five Format branches and direct-IRI hasFormat; move codecs into independent trees, with optional DigitalStream descriptions on Item or Carrier. Stream nodes group codecs, language usage, and colour/sound characteristics. Storage/content and package composition remain open with §4.8; legacy mapping migration is not complete. The issue descriptions and options above record the pre-decision analysis.
  - **Untested trees**: still pending discussion.

### 4.10 Format and Optional Digital Streams
- **Status**: **ONTOLOGY IMPLEMENTED; mapping migration and Carrier architecture remain open**
- **Decision**:
  - Preserve FilmFormat, AudioFormat, VideoFormat, DataStorageFormat, and DigitalFormat under Format. No CarrierFormat wrapper, hasCarrierFormat/hasDigitalFormat split, or change to blank-node hasFormat values.
  - VideoCodec and AudioCodec are independent trees and SKOS schemes, preserving codec IRIs. Codec subclass links to DigitalFormat are removed.
  - Add DigitalStream with VideoStream, AudioStream, and SubtitleStream. `hasStream` has domain Item ∪ Carrier and range DigitalStream. Both inventory levels are first-class, not a mandatory Item→Carrier hierarchy.
  - Add hasVideoCodec on VideoStream and hasAudioCodec on AudioStream. Extend hasColourCharacteristic to VideoStream and hasSoundCharacteristic to AudioStream, retaining their existing domains.
  - Extend hasLanguageUsage to Item and DigitalStream while retaining Work, Variant, Manifestation. A stream can reference the same LanguageUsage node as the W/V/M/I description. No automatic inheritance is asserted.
- **Rationale**:
  - A codec describes encoding, not track identity. Container-level codec lists cannot bind different audio streams to their languages and channel layouts. One stream node per independently described stream solves this; one multichannel stream is not several streams merely because it has several channels.
  - EBUCore's MediaResource/Track distinction and track-level codec/language description provide inspiration ([ontology source](https://github.com/ebu/ebucore/blob/master/ebucore.rdf)). Do not import its whole engineering model or assume its Format naming matches FIAFcore.
  - Explicit digital-only streams avoid repurposing ColourCharacteristic as a picture-track entity or forcing unfamiliar track descriptions onto film. Ordinary film format/colour/sound descriptions remain unchanged.
  - File and storage carrier are different objects. Separating them is preferred over adding facet properties to excuse mixing LTO and MKV on one unit. Aggregate holdings may still summarise component formats.
  - A dedicated stream layer is optional and distinct from inventory entities; it can use blank nodes. No archive needs to create Carrier records simply to describe a digital file's streams.
- **Deliberate limits**:
  - No Manifestation-domain hasStream, generic analogue track model, new storage/content or package-part relationships, technical measurement family, subtitle codec taxonomy, cardinality/disjointness constraints, or changes to Carrier's definition.
  - Domain/range statements infer types rather than prohibit invalid data. Further SHACL validation is a separate decision.
  - Multiple containers on a summary record do not establish which streams belong to which file. Use distinct object descriptions where those associations are known. Unknown stream inventories may be omitted.
- **Migration still to review**:
  - BFI emits ProRes422HQ and ProRes via hasFormat on Manifestation. Do not attach hasStream there, silently drop codec information, or invent Item holdings to accommodate it. These legacy triples remain pending a source-level mapping decision.
  - Bundesarchiv MPEG-2 on Item can map to a minimally described VideoStream, but source data and execution must be checked before a broader transform migration. Existing storage/file mixing likewise remains a §4.8 mapping issue.
  - Existing codec-as-format queries require updating; moving codec IRIs does not preserve their former Format ancestry. No compatibility subclass links or automatic assertion propagation are added.
- **Documentation/examples**: `FORMAT_TAXONOMY.md` contains the full tree and rationale; `TAXONOMY_OVERVIEW.md` summarises it; `example/DigitalStream.ttl` illustrates Item-only and Carrier-level files, shared language usages, subtitles, and unchanged film carriers. See §4.8 for the independent Carrier reassessment.

---

## Part 5: Candidate Expansions Through the Same Lens

### 5.1 `Form` and `Genre` (`fiafcore-form.ttl` & `fiafcore-genre.ttl`)
- **Status**: **OPEN**
- **Scope**:
  - **Missing core classes across BFI, BA, and NB**: `Documentary` / `DocumentaryFilm`, `Newsreel` (`Wochenschau`), `TelevisionFilm` (`Fernsehfilm` / `Fjernsynsfilm`), `AdvertisingFilm` / `Commercial` (`Werbefilm` / `Reklame`), `MusicVideo`.
  - **Dropped matches in `bundesarchiv.xsl` (lines 1028–1245)**: ~35 German genre terms in `bundesarchiv.xsl` are currently dropped with empty `<xsl:when>` clauses even though exact FIAFcore classes already exist in `fiafcore-genre.ttl` (`Abenteuerfilm`, `Horrorfilm`, `Science_Fiction`, `Western`, `Melodram`, `Tragödie`, `Biografischer_Film`, `Historischer_Film`, `Experimentalfilm`, `Naturfilm`, `Umweltfilm`, `Ethnografischer_Film`, etc.).
  - **Structural review**: Clarify the boundary between `Form` and `Genre` and evaluate whether `Genre`'s 68 flat classes should be grouped into intermediate categories.
  - **Facet check first**: Both trees currently mix different kinds of things (see **§4.9**). Decide which facets belong in `Form` (length, publication/structural mode, production context, production-material purpose) and in `Genre` (narrative/thematic genre, technique/medium, movement/style, purpose/context, audience, adaptation status) before adding new concepts.
- **Resolution**: *Pending discussion.*

---

### 5.2 `LanguageUsage` (`fiafcore-languageusage.ttl`)
- **Status**: **OPEN**
- **Scope**:
  - Distinguish Original vs. Dubbed dialogue (`Dialogue (original)` vs `Dialogue (dubbed)` in BFI; `Originalspråk` vs `Dubbing` in NB; `Sprache` vs `Synchronisation` in BA).
  - Add Commentary / Narration (`Kommentarton` in BA), Audio Description (`Synstolking` in NB, `Audiodeskription` in BA), and clarify SDH / Closed Captions (`Captions` vs `Subtitles`).
  - **Facet check first**: `LanguageUsage` currently mixes modality (`SpokenLanguage`, `SungLanguage`, `SignedLanguage`), written placement (`Subtitles`, `Intertitles`, `Captions`, `Credits`), and absence (`NoDialogue`). Adding original vs. dubbed and audio description/commentary would introduce translation status and accessibility function into the same tree; determine the facets before extending it (see **§4.9**).
- **Resolution**: *Pending discussion.*

---

### 5.3 `Activity` Mappings (`fiafcore-activity.ttl` & `bundesarchiv.xsl`)
- **Status**: **OPEN**
- **Scope**:
  - Map the ~30 German credit roles in `bundesarchiv.xsl` (lines 417–988) that currently fall back to generic `fiaf:Activity` despite having exact classes in `fiafcore-activity.ttl` (`Producer`, `ExecutiveProducer`, `Coproducer`, `CameraOperator`, `ProductionDesigner`, `Choreographer`, `GafferLighting`, `SpecialEffects`, `Interviewer`, `Continuity`, `DubbingMixer`, `FoleyArtist`, `Double`, etc.).
- **Resolution**: *Pending discussion.*

---

### 5.4 `Base` and `Stock` Expansions (`fiafcore-base.ttl` & `fiafcore-stock.ttl`)
- **Status**: **OPEN**
- **Scope**:
  - `Base`: Evaluate adding `PolycarbonateBase` (for optical discs: `Polycarbonat` in BA), `PaperBase` (`Papir` in NB, n=3,290), `GlassBase` (`Glass` in NB), `CellophaneBase` (`Ozaphan` in BA). Update `fiaf:hasBase` description in `fiafcore-item.ttl` (which still says *"The physical material or video format..."*).
  - `Stock`: Evaluate adding remaining stock manufacturers dropped in `BFI_FIAF_LOD_Items.xsl` (`Ampex`, `Pyral`, `Zonal`, `Perutz`, `Svema`, `Ansco`, `Sakura`, `Memorex`, `EMTEC`, `JVC`).
- **Resolution**: *Pending discussion.*

---

### 5.5 Image Geometry, Technical Characteristics & Fixity (`AspectRatio`, `FrameRate`, `Resolution`, `BitDepth`, `Checksum`)
- **Status**: **OPEN**
- **Scope**:
  - Address unmapped technical and fixity fields across NB (`ONTOLOGY_GAPS.md` #4 `aspect_ratio` n=42k, #5 `frame_rate` n=12k, #10 `resolution`/`bit_depth`/`bit_rate`/`sample_rate`/checksum), BA (`ba:SDHDFernsehnorm` = `1080i/25`, `1080p/25`), and BFI (`Scope`, `Super-35`, `Imax`, `3-D`, `High-Definition Video`).
  - Decide whether stream/file-level technical metrics (`frameRate`, `aspectRatio`, `width`/`height`, `bitDepth`, `bitRate`, `sampleRate`, file `checksum`/`hash`) attach directly to `fiaf:Item`, to a `fiaf:TechnicalCharacteristic` node, or to component track `Item`s in multi-file digital packages (`DCP`, `IMF`; see **§4.8** and `CARRIER_AND_DIGITAL_MODELING.md` §2.4 & §7.4).
- **Resolution**: *Pending discussion.*

---

### 5.6 NB (`MAPPING.md`) Alignment with `unified-taxonomy`
- **Status**: **OPEN**
- **Scope**:
  - Update NB transform tables and `MAPPING.md` to use the new classes in `unified-taxonomy`:
    - `ColourStandard` (`Tinted`, `Toned` via `hasColourProcess`) and `ColourEncoding` (`RGB`, `YUV` via `hasColourEncoding`)
    - `Format` (`28mmFilm`, `VHS`, `SuperVHS`, `Betamax`, `VCR`, `Video8`, `Hi8`, `Video2000`, `Umatic*`, `DVCAM`, `DVCPRO`, `MiniDV`, `HDV`, `HDCAM`, `D3`, `D6`, `CDR`, `DVDR`, `UltraHDBluRay`, `DAT`, `DTRS`, `LTO2`..`LTO6`, `HardDrive`, `MagnetoOpticalDisc`, `FlashMemory`, `DCP`)
    - `Element` (`Negative`, `ColourReversalIntermediate`, `ReversalPositive`, `WorkPrint`, `SeparatedMagneticSound`)
    - `SoundStandard`, `NoiseReduction` & `SoundChannelConfiguration` (`Mono`, `DolbyA`, `DolbySR` via `hasNoiseReduction`, `FourTrackMagnetic`, `SixTrackMagnetic`, `DolbyDigitalSurroundEX`)
    - `Country` (`SovietUnion`, `Yugoslavia`) and `Stock` (`Maxell`, `BASF`, `Scotch`, `TDK`)
- **Resolution**: *Pending discussion.*
