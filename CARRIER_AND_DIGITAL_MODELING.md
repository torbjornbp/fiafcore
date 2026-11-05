# Working Document: Digital Files, Storage Media, and Replacing `Carrier` with Partitive `Item`s

> Historical architectural analysis, not an adopted Carrier redesign. The later Format decision adds optional `DigitalStream` descriptions directly on Item or Carrier and moves codecs out of Format; see `FORMAT_TAXONOMY.md` and `TAXONOMY_REVIEW.md` §4.10. Examples below retain the earlier codec-as-format and proposed storage/part relationships for context. Carrier reassessment (§4.8), storage/content links, and package composition remain open; the stream decision does not select any of the competing architectures below.

## 1. Context & Motivation

This document captures research and brainstorming comparing **FIAFcore**, **EBUCore**, and **FRBR / IFLA LRM / RDA** on two closely related modelling questions:

1. How FIAFcore models **digital files, containers, codecs, and digital storage media** compared to EBUCore.
2. Whether **`fiaf:Carrier` should be removed** and replaced with recursive **`fiaf:Item`** whole–part relationships (`hasPart` / `isPartOf`), aligning FIAFcore with EBUCore's `MediaResource` pattern, RDA/FRBR's `Item` whole–part relationships, and the four-entity model of the FIAF Moving Image Cataloguing Manual.

---

## 2. FIAFcore vs. EBUCore: Digital Files & Digital Storage Media

### 2.1 Core Entity Architecture

| Aspect | FIAFcore (Current) | EBUCore / EBUCorePlus |
| :--- | :--- | :--- |
| **Conceptual Spine** | `Work` → `Variant` → `Manifestation` → `Item` → `Carrier` | `EditorialObject` (`BusinessObject`) → `MediaResource` (with `hasPart` / `isPartOf` and `hasTrack`) |
| **Digital Holding Entity** | `fiaf:Item` (typed via `fiaf:isElement` as `DigitalMaster`, `DigitalMezzanine`, `DigitalAccessCopy`) | `ebucore:MediaResource` |
| **Discrete Unit / Part** | `fiaf:Carrier` (reels, cans, or digital file parts) | Child `ebucore:MediaResource` (via `ebucore:hasPart` / `ebucore:isPartOf`) |
| **Streams / Tracks** | No track entity; colour, sound, and codec properties attach directly to `Manifestation` or `Item` | `ebucore:Track` (`VideoTrack`, `AudioTrack`, `DataTrack`, `TimecodeTrack`) attached to `MediaResource` |

### 2.2 Containers, Packages, Image Sequences, and Codecs

In **FIAFcore** (`ontology/fiafcore-format.ttl`), all digital format layers are subclasses of `fiaf:Format` (under `fiaf:DigitalFormat`) and are attached using a single predicate, **`fiaf:hasFormat`**:

* **`fiaf:ContainerFormat`**: `AVI`, `MKV`, `MOV`, `MP4`, `MXF`, `Quicktime`, `VOB`, `WAV`, `WebM`
* **`fiaf:ImageFormat`**: `Cineon`, `DPX`, `OpenEXR`, `TIFF`
* **`fiaf:PackageFormat`**: `DCDM`, `DCP`, `IMF`
* **`fiaf:VideoCodec`**: `FFV1`, `MPEG2`, `MPEG-4`, `ProRes` (`ProRes422HQ`), `RealVideo`, `WindowsMedia`
* **`fiaf:AudioCodec`**: `PCM`

A single `Item` or `Manifestation` representing a QuickTime ProRes file asserts multiple `fiaf:hasFormat` statements:

```turtle
<item> a fiaf:Item ;
    fiaf:hasFormat fiaf:Quicktime , fiaf:ProRes422HQ .
```

In **EBUCore**, each technical layer has a distinct class and property:
* **Container / File**: `ebucore:hasContainerFormat` / `ebucore:hasMimeType` / `ebucore:hasFileFormat`
* **Essence / Stream**: `ebucore:VideoFormat` and `ebucore:AudioFormat` (which describe the encoded video/audio streams—whereas in FIAFcore, `fiaf:VideoFormat` and `fiaf:AudioFormat` mean *physical* video/audio carriers like VHS or 1/4" tape)
* **Codec**: `ebucore:hasCodec` / `ebucore:hasEncodingFormat` → `ebucore:Codec`

### 2.3 Digital Storage Media (LTO, Hard Drives, Optical Data Discs, Flash)

* **FIAFcore**: Models offline digital storage media as subclasses of **`fiaf:Format`** under **`fiaf:DataStorageFormat`**:
  * `fiaf:CDR`, `fiaf:DVDR` (distinct from `fiaf:CD` under `AudioFormat` and `fiaf:DVD`/`fiaf:BluRay` under `VideoFormat > OpticalVideoDisc`)
  * `fiaf:LTO` (`LTO2`, `LTO3`, `LTO4`, `LTO5`, `LTO6`)
  * `fiaf:HardDrive`
  * `fiaf:FlashMemory`
  * `fiaf:MagnetoOpticalDisc`
  * Because `fiaf:hasFormat` has domain `Manifestation ∪ Item ∪ Carrier`, transforms currently attach both the file format (`MXF`, `DPX`) and the physical storage format (`LTO5`, `HardDrive`) via `fiaf:hasFormat` on the `Item`.
* **EBUCore**: Separates the **file/format** of the `MediaResource` from the **storage medium** (`ebucore:StorageType` / EBU Storage Media SKOS vocabulary: HDD, SSD, LTO tape, optical disc, flash memory, server/cloud storage) and physical/network `ebucore:locator`.

### 2.4 Technical & File-Level Characteristics

| Characteristic | FIAFcore | EBUCore |
| :--- | :--- | :--- |
| **File Size** | `fiaf:hasExtent` → `Kilobyte`, `Megabyte`, `Gigabyte`, `Terabyte` + `hasExtentValue` | `ebucore:fileSize` (integer bytes on `MediaResource`) |
| **Digital Colour** | `fiaf:ColourCharacteristic` → `hasColourSpace` (`Rec601`, `Rec709`, `Rec2020`, `DCIP3`, `ACES2065_1`, `sRGB`), `hasColourEncoding` (`RGB`, `YUV`, `XYZ`, `Greyscale`), `hasTransferFunction` (`Gamma`, `PQ`, `HLG`, `Logarithmic`, `Linear`) | Attached to `ebucore:VideoFormat` / `VideoTrack` |
| **Technical Metrics & Fixity** | Not yet modeled (see `ONTOLOGY_GAPS.md` #4, #5, #10: aspect ratio, frame rate, resolution, bit depth, bitrate, sample rate, checksum/hash) | Native properties on `MediaResource` / `Format` (`hash`, `locator`, `bitRate`, `frameRate`, `sampleRate`, `width`, `height`, `bitDepth`, `aspectRatio`) |

---

## 3. FIAFcore vs. EBUCore: Analog Materials (e.g. Film Reels)

Because **EBUCore** originated in broadcast engineering, it models a physical film reel using the same `ebucore:MediaResource` class as a digital file:
* A multi-reel film print is a parent `ebucore:MediaResource` linked to per-reel `ebucore:MediaResource` children via **`ebucore:hasPart` / `ebucore:isPartOf`**.
* The film gauge (`35mm film`, `16mm film`, etc.) is a SKOS concept from the EBU Storage Media vocabulary attached via `ebucore:hasMedium` / `ebucore:hasStorageType`.
* Image and sound on the reel are modeled as `ebucore:VideoTrack` and `ebucore:AudioTrack`.
* **EBUCore lacks native photochemical concepts**: it has no classes or properties for film base chemistry (`NitrateBase`, `AcetateBase`, `PolyesterBase`), film stock brands (`Kodak`, `Agfa`, `Orwo`), photochemical generation (`OriginalNegative`, `DuplicateNegative`, `ColourSeparationNegative`, `DyeTransferMatrix`, `AnswerPrint`, `ReleasePrint`), historical colour processes (`Tinted`, `Toned`, `StencilColouring`, `Technicolor`, `Dufaycolor`), or optical film sound (`OpticalVariableDensity`, `OpticalVariableArea`).

**FIAFcore** excels at all of these photochemical distinctions, but attaches them exclusively to **`fiaf:Item`** (or `Manifestation`), leaving **`fiaf:Carrier`** almost empty.

---

## 4. Proposal: Replace `fiaf:Carrier` with Partitive `fiaf:Item` (`hasPart` / `isPartOf`)

### 4.1 Lineage: FRBR → RDA → FIAF Manual → FIAFcore

1. **FIAF Moving Image Cataloguing Manual (2016)**:
   * The FIAF Manual—which was "forked" from FRBR—defines **four core entities**: **Work, Variant, Manifestation, and Item**.
   * `Carrier` is *not* a primary entity in the FIAF Manual (notably, `ontology/fiafcore-carrier.ttl` has no `dc:source` citation to the FIAF Manual, unlike `Work`, `Variant`, `Manifestation`, and `Item`).
2. **FRBR / IFLA LRM / RDA (`rdai:P40009` & `rdai:P40034`)**:
   * In FRBR, IFLA LRM, and RDA, an **Item** (`rdac:C10003`) may consist of one physical/digital object or multiple objects (e.g., a multi-reel film print, a multi-cassette video recording, or a multi-file digital package).
   * When cataloguers need to describe discrete components or containers at the Item level (such as an individual reel, a component digital file, or a shared storage container), RDA models both sides as **Items** connected via **Item-to-Item relationships** under [`rdai:P40046`](http://rdaregistry.info/Elements/i/P40046) (*"has related item of item"* / altLabel: *"whole-part item relationship"*):
     * **[`rdai:P40009`](https://www.rdaregistry.info/Elements/i/#P40009)** (`rdai:containedInItem.en` — **"is contained in item"**):
       > *"Relates an item to an item that is a larger item of which an item is a discrete component."*
       > (Domain: `Item`, Range: `Item`)
     * **[`rdai:P40034`](https://www.rdaregistry.info/Elements/i/#P40034)** (`rdai:containerOfItem.en` — **"is container of item"**):
       > *"Relates an item to an item that is a discrete component of a larger item."*
       > (Inverse of `rdai:P40009`; Domain: `Item`, Range: `Item`)
     * Related sibling properties under `rdai:P40046` for horizontal combinations (such as compilation reels or shared containers):
       * **[`rdai:P40029`](https://www.rdaregistry.info/Elements/i/#P40029)** (`rdai:heldWith.en` — **"is held with"**): *"Relates an item to an item that is held in the same collection as an item."*
       * **[`rdai:P40032`](https://www.rdaregistry.info/Elements/i/#P40032)** (`rdai:boundWith.en` — **"is bound with"**): *"Relates an item to an item that is physically combined with an item to form a collection manifestation."*
       * **[`rdai:P40163`](https://www.rdaregistry.info/Elements/i/#P40163)** (`rdai:onManifestationWith.en` — **"is on manifestation with"**): *"Relates an item to an item that is reproduced on the same manifestation as an item."*
3. **EBUCore**:
   * Uses the exact same recursive pattern on `ebucore:MediaResource` via `ebucore:hasPart` and `ebucore:isPartOf`.

### 4.2 Why `fiaf:Carrier` is Problematic Today

Currently in FIAFcore:
* `fiaf:Carrier` can **only** take three properties: `fiaf:hasIdentifier`, `fiaf:hasEvent`, and `fiaf:hasFormat`.
* Meanwhile, the following properties have domain `fiaf:Item` (or `Manifestation ∪ Item`), and **cannot** be used on `fiaf:Carrier`:
  * `fiaf:hasBase` (`NitrateBase`, `AcetateBase`, `PolyesterBase`)
  * `fiaf:hasStock` (`Agfa`, `Kodak`, `Orwo`, etc.)
  * `fiaf:hasExtent` (`Foot`, `Metre`, `Minute`, `Second`, `Gigabyte`, etc.)
  * `fiaf:hasColourCharacteristic` (e.g. `BlackAndWhite`, `Colour`, `Tinted`, `Toned`)
  * `fiaf:hasSoundCharacteristic`
  * `fiaf:hasStatus` (`Preservation`, `Access`)
  * `fiaf:isElement`
  * `fiaf:hasHoldingInstitution`

In real archival collections, **material properties frequently vary at the reel or file-part level**:
* **Composite / spliced film items**: Reel 1–3 of a print may be on `NitrateBase` (`Kodak`), while Reel 4 is a later replacement reel on `AcetateBase` (`Agfa`).
* **Reel-by-reel extent and colour**: Each reel has its own length in feet/metres and duration; Reel 2 may contain a `Tinted` sequence while Reel 1 is purely `BlackAndWhite`.
* **Picture + sound follower pairs**: An Item or preservation set may comprise a picture reel (`35mmFilm`, `OriginalNegative`) and a separate sound reel (`35mmMagneticFilm`, `SeparatedMagneticSound`).
* **Multi-file digital packages (DCP, IMF, DPX sequences)**: A DCP Item is a package (`fiaf:DCP`) whose constituent parts are a video track file (`fiaf:MXF`), an audio track file (`fiaf:MXF`, `fiaf:PCM`), and subtitle/CPL XML files, potentially spanning multiple `LTO` tapes or `HardDrive`s.

If `Carrier` is kept as a separate class, FIAFcore would eventually have to duplicate almost every `Item` property onto `Carrier`.

### 4.3 How Recursive `fiaf:Item` (`hasPart` / `isPartOf`) Solves This

By removing `fiaf:Carrier` and introducing whole–part properties on `fiaf:Item` (e.g. `fiaf:hasPart` / `fiaf:isPartOf`, or broader whole–part properties usable across WEMI levels):

1. **Every reel, can, cassette, LTO tape, or component digital file is simply a `fiaf:Item`** that is `isPartOf` a parent `fiaf:Item`.
2. **Full descriptive power at any granularity**:
   * An archive with only summary item-level data (like BFI) records a single `fiaf:Item` with `hasExtent` (`5 Reels`, `4500 Feet`).
   * An archive with reel-level or file-level records (like Bundesarchiv's `Aufbewahrungseinheit`) maps each unit to a child `fiaf:Item` linked via `fiaf:hasPart`, and can attach reel-specific `hasBase`, `hasStock`, `hasExtent`, `hasFormat`, `hasEvent`, and `hasIdentifier` directly to each part.
3. **Simpler Ontology**:
   * Eliminates `ontology/fiafcore-carrier.ttl` and removes `Carrier` from ` owl:unionOf` domains in `hasFormat`, `hasEvent`, and `hasIdentifier`.
   * Aligns strictly with the 4-entity FIAF Manual (`Work`, `Variant`, `Manifestation`, `Item`).

---

## 5. Sketch Examples Using Partitive `Item`s

### Example A: Multi-Reel Film Print with Mixed Base/Stock per Reel

```turtle
@prefix fiaf: <https://dev.fiafcore.org/> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

<https://example.fiafcore.org/item/print-1>
    a fiaf:Item ;
    rdfs:label "Metropolis Release Print (2 Reels)" ;
    fiaf:isElement fiaf:ReleasePrint ;
    fiaf:hasFormat fiaf:35mmFilm ;
    fiaf:hasStatus fiaf:Preservation ;
    fiaf:hasHoldingInstitution <https://example.fiafcore.org/agent/archive> ;
    fiaf:hasPart
        <https://example.fiafcore.org/item/print-1-reel-1> ,
        <https://example.fiafcore.org/item/print-1-reel-2> .

<https://example.fiafcore.org/item/print-1-reel-1>
    a fiaf:Item ;
    rdfs:label "Reel 1" ;
    fiaf:isPartOf <https://example.fiafcore.org/item/print-1> ;
    fiaf:hasBase fiaf:NitrateBase ;
    fiaf:hasStock [ a fiaf:Agfa ] ;
    fiaf:hasColourCharacteristic [
        a fiaf:BlackAndWhite ;
        fiaf:hasColourProcess fiaf:Tinted
    ] ;
    fiaf:hasExtent [
        a fiaf:Metre ;
        fiaf:hasExtentValue "310"
    ] .

<https://example.fiafcore.org/item/print-1-reel-2>
    a fiaf:Item ;
    rdfs:label "Reel 2 (Later safety replacement)" ;
    fiaf:isPartOf <https://example.fiafcore.org/item/print-1> ;
    fiaf:hasBase fiaf:AcetateBase ;
    fiaf:hasStock [ a fiaf:Kodak ] ;
    fiaf:hasColourCharacteristic [ a fiaf:BlackAndWhite ] ;
    fiaf:hasExtent [
        a fiaf:Metre ;
        fiaf:hasExtentValue "295"
    ] .
```

### Example B: Digital Package (`DCP` or Preservation Master) with Component Files

```turtle
@prefix fiaf: <https://dev.fiafcore.org/> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

<https://example.fiafcore.org/item/dcp-1>
    a fiaf:Item ;
    rdfs:label "Metropolis Restored DCP" ;
    fiaf:isElement fiaf:DigitalMaster ;
    fiaf:hasFormat fiaf:DCP ;
    fiaf:hasPart
        <https://example.fiafcore.org/item/dcp-1-video> ,
        <https://example.fiafcore.org/item/dcp-1-audio> .

<https://example.fiafcore.org/item/dcp-1-video>
    a fiaf:Item ;
    rdfs:label "DCP Picture Track (MXF)" ;
    fiaf:isPartOf <https://example.fiafcore.org/item/dcp-1> ;
    fiaf:hasFormat fiaf:MXF ;
    fiaf:hasColourCharacteristic [
        a fiaf:BlackAndWhite ;
        fiaf:hasColourEncoding fiaf:XYZ ;
        fiaf:hasColourSpace fiaf:DCIP3 ;
        fiaf:hasTransferFunction fiaf:Gamma
    ] ;
    fiaf:hasExtent [
        a fiaf:Gigabyte ;
        fiaf:hasExtentValue "84"
    ] .

<https://example.fiafcore.org/item/dcp-1-audio>
    a fiaf:Item ;
    rdfs:label "DCP Audio Track (MXF/PCM)" ;
    fiaf:isPartOf <https://example.fiafcore.org/item/dcp-1> ;
    fiaf:hasFormat fiaf:MXF , fiaf:PCM ;
    fiaf:hasSoundCharacteristic [
        a fiaf:Sound ;
        fiaf:hasSoundChannelConfiguration fiaf:Surround
    ] ;
    fiaf:hasExtent [
        a fiaf:Gigabyte ;
        fiaf:hasExtentValue "4.2"
    ] .
```

---

## 6. Untangling `DigitalFormat` vs. `DataStorageFormat`: Work-Independent Storage Carriers

A major tension in the current ontology is that `fiaf:DigitalFormat` (`MXF`, `MP4`, `ProRes`, `DPX`, `DCP`) and `fiaf:DataStorageFormat` (`LTO5`, `LTO6`, `HardDrive`, `FlashMemory`, `DVDR`) are both attached to the same `Item` via `fiaf:hasFormat`.

In practice, an offline digital storage medium like an **LTO tape** or **hard drive** is **not** an embodiment of a single `Work` or `Manifestation`:
* **Many-to-One (Shared Storage Carrier)**: A single LTO-6 tape or hard drive in the vault frequently holds digital files belonging to **multiple different Works/Manifestations** (e.g., 20 short films archived onto one LTO tape).
* **One-to-Many (Multi-Tape Package)**: Conversely, a single 4K uncompressed `DPX` scan of a feature film may span **multiple LTO tapes**.

Using `fiaf:isPartOf` / `fiaf:hasPart` cleanly resolves this by separating the **digital file Item** (which belongs to a `Work` / `Manifestation`) from the **data storage carrier** (which is a physical archival object in the repository, **not** attached under any single `Work` / `Manifestation`):

```text
Work A ──hasManifestation──► Manifestation A ──hasItem──► File Item A (MKV / FFV1) ──┐
                                                                                     ├──isPartOf──► Storage Carrier (LTO-6 Tape #0042)
Work B ──hasManifestation──► Manifestation B ──hasItem──► File Item B (MOV / ProRes) ┘              (not under any Work/Manifestation)
```

### Why This Works So Well
1. **Clean Separation of Formats**:
   * The **File `Item`** (under `Manifestation`) carries only `fiaf:DigitalFormat`s (`MKV`, `FFV1`, `PCM`), `fiaf:DigitalElement` (`DigitalMaster`), `ColourCharacteristic`, `SoundCharacteristic`, and file size (`Gigabyte`).
   * The **Storage Carrier** (not under any `Work`/`Manifestation`) carries `fiaf:DataStorageFormat` (`LTO6`, `HardDrive`), its physical vault barcode (`hasIdentifier`), `hasHoldingInstitution`, physical storage `hasEvent` (e.g., LTO migration or tape inspection), and total tape capacity (`Terabyte`).
2. **Handles Many-to-One and One-to-Many Naturally**:
   * **Many files on one LTO tape**: Multiple file `Item`s (from different Works) each assert `fiaf:isPartOf <lto-tape-0042>`.
   * **One large scan across multiple LTO tapes**: A parent `DPX` `Item` (under the `Manifestation`) has part `Item`s (Reel 1 DPX sequence, Reel 2 DPX sequence), where Reel 1 `isPartOf <lto-tape-0042>` and Reel 2 `isPartOf <lto-tape-0043>`.
3. **Analog Parallel (Compilation Reels)**:
   * The exact same pattern solves the classic film archive problem of **compilation cans/reels**, where prints of three separate short films (`Work A`, `Work B`, `Work C`) are spliced onto a single physical 35mm reel in the vault. Each short film's copy is an `Item` under its respective `Work`/`Manifestation`, and each `isPartOf` the shared physical reel!

### Example C: Digital Files Under Different Works Stored on a Shared Work-Independent LTO Tape

```turtle
@prefix fiaf: <https://dev.fiafcore.org/> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

# --- Work 1 & its Digital File Item ---

<https://example.fiafcore.org/work/1>
    a fiaf:Work ;
    rdfs:label "Workers Leaving the Lumière Factory" ;
    fiaf:hasManifestation <https://example.fiafcore.org/manifestation/1> .

<https://example.fiafcore.org/manifestation/1>
    a fiaf:PreservationManifestation ;
    fiaf:hasItem <https://example.fiafcore.org/item/file-1> .

<https://example.fiafcore.org/item/file-1>
    a fiaf:Item ;
    rdfs:label "Preservation Master File (FFV1/MKV)" ;
    fiaf:isElement fiaf:DigitalMaster ;
    fiaf:hasFormat fiaf:MKV , fiaf:FFV1 ;
    fiaf:hasExtent [
        a fiaf:Gigabyte ;
        fiaf:hasExtentValue "12.5"
    ] ;
    fiaf:isPartOf <https://example.fiafcore.org/storage/lto-0042> .

# --- Work 2 & its Digital File Item ---

<https://example.fiafcore.org/work/2>
    a fiaf:Work ;
    rdfs:label "The Arrival of a Train" ;
    fiaf:hasManifestation <https://example.fiafcore.org/manifestation/2> .

<https://example.fiafcore.org/manifestation/2>
    a fiaf:PreservationManifestation ;
    fiaf:hasItem <https://example.fiafcore.org/item/file-2> .

<https://example.fiafcore.org/item/file-2>
    a fiaf:Item ;
    rdfs:label "Preservation Master File (FFV1/MKV)" ;
    fiaf:isElement fiaf:DigitalMaster ;
    fiaf:hasFormat fiaf:MKV , fiaf:FFV1 ;
    fiaf:hasExtent [
        a fiaf:Gigabyte ;
        fiaf:hasExtentValue "14.1"
    ] ;
    fiaf:isPartOf <https://example.fiafcore.org/storage/lto-0042> .

# --- Work-Independent Data Storage Carrier (LTO Tape) ---

<https://example.fiafcore.org/storage/lto-0042>
    a fiaf:Item ; # or a dedicated DataStorageCarrier class if distinguished from WEMI Items
    rdfs:label "Vault LTO-6 Tape #0042" ;
    fiaf:hasFormat fiaf:LTO6 ;
    fiaf:hasHoldingInstitution <https://example.fiafcore.org/agent/archive> ;
    fiaf:hasIdentifier [
        a fiaf:Identifier ;
        fiaf:hasIdentifierValue "LTO-0042"
    ] ;
    fiaf:hasPart
        <https://example.fiafcore.org/item/file-1> ,
        <https://example.fiafcore.org/item/file-2> .
```

---

## 7. Counterpoint: Collection Quantification, the Single-Reel Wrapper Problem, and Retaining `fiaf:Carrier`

### 7.1 The Collection Quantification Problem ("How Many Copies vs. How Many Reels?")

Merging the grouping entity (`fiaf:Item`) and the physical shelf/storage unit (`fiaf:Carrier`) into a single recursive `fiaf:Item` class introduces a serious practical drawback for **collection quantification and SPARQL querying**:

Archives routinely need to answer two distinct inventory questions:
1. *"How many copies / elements (`Item`s) of Works do we hold?"*
   ```sparql
   SELECT (COUNT(?item) AS ?copies) WHERE { ?item a fiaf:Item }
   ```
2. *"How many physical film reels, videocassettes, or LTO tapes (`Carrier`s) do we have on our vault shelves?"*
   ```sparql
   SELECT (COUNT(?carrier) AS ?shelfUnits) WHERE { ?carrier a fiaf:Carrier }
   ```

If both a 5-reel print and its 5 individual reels are typed as `fiaf:Item`:
* **Double-counting**: A single 5-reel print produces **6 `fiaf:Item` nodes** (1 parent + 5 children), so `COUNT(?item a fiaf:Item)` returns neither the number of copies (1) nor the number of reels (5).
* **Fragile `FILTER NOT EXISTS` queries**: Every query has to filter by graph topology (`FILTER NOT EXISTS { ?item fiaf:isPartOf ?parent }` or `FILTER NOT EXISTS { ?item fiaf:hasPart ?child }`), which is slower on large graphs and **breaks down when the hierarchy direction inverts**:
  * For a **multi-reel print**, the parent is the copy (`Item`) and the 5 children are the physical reels (`Carrier`s).
  * For a **shared LTO tape or compilation film reel**, the parent container is the physical unit (`LTO6` tape or compilation reel) and the 20 children are the individual work copies (`Item`s)!
  * Consequently, neither "root `Item`s" nor "leaf `Item`s" reliably correspond to either archival copies or physical shelf units.

---

### 7.2 The Single-Reel / Single-Unit Wrapper Problem (`1 Item` + `1 ITEM_PART`)

Conversely, when a cataloguing system strictly enforces a two-layer `Item → Carrier` (`ITEM → ITEM_PART`) hierarchy for every holding:
* Every **single-reel short film**, **single videocassette** (`VHS`, `DigitalBetacam`), **single optical disc** (`DVD`, `BluRay`), or **single digital file** (`MP4`) requires creating **1 `Item` record plus 1 redundant `ITEM_PART` (`Carrier`) record** below it solely so that `Carrier`-level inventory counts include single-unit items.
* For single-unit holdings, that extra wrapper layer adds cataloguing friction and duplicates metadata without adding real structural information.

### 7.3 Solving Both Problems: Retaining `fiaf:Carrier` + Direct Single-Unit Holdings

We can keep the best of both worlds—**exact SPARQL counts for both `Item` and `Carrier`**, **full reel-level description**, **many-to-one shared LTO tapes/compilation reels**, and **no redundant wrapper records for single-reel holdings**—through an enriched `fiaf:Carrier` model:

1. **Expand Reel-Variable Property Domains to Include `fiaf:Carrier`**:
   * Add `fiaf:Carrier` to the `owl:unionOf` domains of `hasBase`, `hasStock`, `hasExtent`, `hasColourCharacteristic`, and `hasSoundCharacteristic` (alongside `hasFormat`, `hasEvent`, and `hasIdentifier`, which already include `Carrier`).
2. **Use `fiaf:hasCarrier` for Both Multi-Reel (`1:N`) and Shared Storage / Compilation (`N:1`) Relationships**:
   * **Multi-reel print (`1 Item ──hasCarrier──► 5 Carriers`)**: 1 `fiaf:Item` links to 5 `fiaf:Carrier`s.
   * **Shared LTO tape or compilation reel (`20 Items ──hasCarrier──► 1 Carrier`)**: 20 digital file `fiaf:Item`s (each under its own `Work`/`Manifestation`, carrying `fiaf:DigitalFormat`) all link via `fiaf:hasCarrier` to **the same** `<lto-tape-0042>` (`a fiaf:Carrier ; fiaf:hasFormat fiaf:LTO6`).
3. **Eliminate the Redundant Wrapper on Single-Unit Holdings (Two Compatible Patterns)**:
   * In the catalog database/UI, allow a single-unit holding (`ITEM_PART` / single-reel item) to sit **directly beneath `Manifestation`** when there is only one physical/digital unit.
   * In FIAFcore RDF, represent that single-unit holding using either:
     * **Pattern 3a — Dual-Typing (`a fiaf:Item, fiaf:Carrier`) on the Single Node**:
       * The single URI under `Manifestation` (`fiaf:hasItem <holding-1>`) is typed as **both** `a fiaf:Item, fiaf:Carrier`.
       * **Why this is so clean**:
         * There is only **1 node** in the RDF graph (no dummy child node).
         * Every `Item` property and every `Carrier` property is valid on it without changing `fiaf:hasItem`.
         * **Collection counts work out of the box**:
           * Given one 5-reel print (`1 Item` + `5 Carriers`) and one 1-reel short film (`1 node typed as a fiaf:Item, fiaf:Carrier`):
           * `COUNT(?x a fiaf:Item)` = **2 copies** (`1 + 1`).
           * `COUNT(?x a fiaf:Carrier)` = **6 physical reels** (`5 + 1`).
     * **Pattern 3b — Allow `fiaf:hasCarrier` Directly on `Manifestation`** (`rdfs:domain [ owl:unionOf (Manifestation Item) ]`):
       * A `Manifestation` can link directly to `fiaf:Carrier` via `fiaf:hasCarrier` when no multi-carrier `Item` grouping exists (though queries counting copies of Manifestations would then check `fiaf:hasItem|fiaf:hasCarrier`).

### Example D: Multi-Reel Print + Single-Reel Holding + Shared LTO Tape (Retaining `fiaf:Carrier` with Dual-Typing)

```turtle
@prefix fiaf: <https://dev.fiafcore.org/> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

# 1. Multi-Reel Feature Print: 1 Item -> 2 Carriers
<https://example.fiafcore.org/manifestation/feature>
    a fiaf:TheatricalManifestation ;
    fiaf:hasItem <https://example.fiafcore.org/item/feature-print> .

<https://example.fiafcore.org/item/feature-print>
    a fiaf:Item ;
    rdfs:label "Feature Film Release Print (2 Reels)" ;
    fiaf:isElement fiaf:ReleasePrint ;
    fiaf:hasFormat fiaf:35mmFilm ;
    fiaf:hasCarrier
        <https://example.fiafcore.org/carrier/feature-reel-1> ,
        <https://example.fiafcore.org/carrier/feature-reel-2> .

<https://example.fiafcore.org/carrier/feature-reel-1>
    a fiaf:Carrier ;
    rdfs:label "Reel 1 (Nitrate, Tinted)" ;
    fiaf:hasFormat fiaf:35mmFilm ;
    fiaf:hasBase fiaf:NitrateBase ;
    fiaf:hasColourCharacteristic [ fiaf:hasColourProcess fiaf:Tinted ] .

<https://example.fiafcore.org/carrier/feature-reel-2>
    a fiaf:Carrier ;
    rdfs:label "Reel 2 (Acetate replacement, B&W)" ;
    fiaf:hasFormat fiaf:35mmFilm ;
    fiaf:hasBase fiaf:AcetateBase ;
    fiaf:hasColourCharacteristic [ a fiaf:BlackAndWhite ] .

# 2. Single-Reel Short Film Directly Under Manifestation: 1 Node (a fiaf:Item, fiaf:Carrier)
<https://example.fiafcore.org/manifestation/short>
    a fiaf:TheatricalManifestation ;
    fiaf:hasItem <https://example.fiafcore.org/item/short-print-reel> .

<https://example.fiafcore.org/item/short-print-reel>
    a fiaf:Item , fiaf:Carrier ;
    rdfs:label "Single-Reel Short Film Print" ;
    fiaf:isElement fiaf:ReleasePrint ;
    fiaf:hasFormat fiaf:16mmFilm ;
    fiaf:hasBase fiaf:AcetateBase .

# 3. Two Digital Master File Items Sharing One Vault LTO-6 Carrier (N Items -> 1 Carrier)
<https://example.fiafcore.org/item/digital-file-1>
    a fiaf:Item ;
    rdfs:label "Feature Preservation Master File (FFV1/MKV)" ;
    fiaf:isElement fiaf:DigitalMaster ;
    fiaf:hasFormat fiaf:MKV , fiaf:FFV1 ;
    fiaf:hasCarrier <https://example.fiafcore.org/carrier/lto-0042> .

<https://example.fiafcore.org/item/digital-file-2>
    a fiaf:Item ;
    rdfs:label "Short Preservation Master File (FFV1/MKV)" ;
    fiaf:isElement fiaf:DigitalMaster ;
    fiaf:hasFormat fiaf:MKV , fiaf:FFV1 ;
    fiaf:hasCarrier <https://example.fiafcore.org/carrier/lto-0042> .

<https://example.fiafcore.org/carrier/lto-0042>
    a fiaf:Carrier ;
    rdfs:label "Vault LTO-6 Tape #0042" ;
    fiaf:hasFormat fiaf:LTO6 .
```

In Example D:
* `?x a fiaf:Item` returns **4 archival holdings** (`feature-print`, `short-print-reel`, `digital-file-1`, `digital-file-2`).
* `?x a fiaf:Carrier` returns **4 physical vault carriers** (`feature-reel-1`, `feature-reel-2`, `short-print-reel`, `lto-0042`).
* `?c a fiaf:Carrier ; fiaf:hasFormat/rdfs:subClassOf* fiaf:FilmFormat` returns the **3 physical film reels** (`feature-reel-1`, `feature-reel-2`, `short-print-reel`).

---

## 8. Open Questions & Brainstorming for Further Research

1. **Should the Work-Independent Storage Container Be a `fiaf:Item` or a Distinct Class (e.g. `DataStorageCarrier` / `StorageMedium`)?**:
   * **Option 1 (Everything is an `Item`)**: The LTO tape or Hard Drive is typed as `fiaf:Item` (with `fiaf:hasFormat fiaf:LTO6`), simply without an incoming `fiaf:hasItem` link from a `Manifestation`.
     * *Pro*: Zero new top-level classes; reuses `hasIdentifier`, `hasHoldingInstitution`, `hasExtent`, `hasEvent`, `hasFormat`, and `hasPart`/`isPartOf`.
     * *Con*: Strictly speaking in FRBR/FIAF Manual definitions, an `Item` is "the physical or digital product of a Manifestation of a Work or Variant", whereas an LTO tape holding 20 films is a storage container rather than a product of a single Manifestation.
   * **Option 2 (Dedicated `StorageCarrier` / `StorageMedium` class, or `DataStorageFormat` as the class of the storage object)**: The file is a `fiaf:Item` (under `Manifestation`), and it links via `fiaf:isPartOf` (or `fiaf:isStoredOn`) to a storage entity that is *not* a `fiaf:Item` (e.g., an instance of `fiaf:LTO6` / `fiaf:DataStorageFormat` directly, or a `fiaf:StorageCarrier` class).
     * *Pro*: Querying `?item a fiaf:Item` only returns actual moving image holdings of works, never raw LTO cartridges or hard drives; and `fiaf:DataStorageFormat` subclasses (`LTO6`, `HardDrive`, `FlashMemory`) could even *be* the classes of those storage carrier instances directly!
2. **Property Naming, Domain, and RDA Alignment (`rdai:P40009` / `rdai:P40034`)**:
   * **RDA-aligned Item-specific properties**:
     * `fiaf:isContainedInItem` (aligned with [`rdai:P40009`](https://www.rdaregistry.info/Elements/i/#P40009) *"is contained in item"*) and its inverse `fiaf:isContainerOfItem` / `fiaf:containsItem` (aligned with [`rdai:P40034`](https://www.rdaregistry.info/Elements/i/#P40034) *"is container of item"*), with domain and range `fiaf:Item`.
     * Notice how RDA's wording (*"container of item"* / *"contained in item"*) works equally well for a 5-reel film print containing Reel 1, a DCP package containing an MXF track, and an LTO tape containing digital file Items!
   * **Generic whole–part properties**:
     * Alternatively, `fiaf:hasPart` and `fiaf:isPartOf` (`owl:inverseOf`) could either be restricted to `fiaf:Item` or have domain/range `Work ∪ Variant ∪ Manifestation ∪ Item` (potentially replacing or specialising `fiaf:hasWork` on `Work`).
3. **Ordering / Sequence of Parts**:
   * How should Reel 1, Reel 2, Reel 3 be ordered when needed? (e.g., via `rdfs:label`, an identifier, or a lightweight `fiaf:hasPartNumber` datatype property).
4. **Stream/Track-Level Technical Properties (EBUCore Inspiration)**:
   * As digital holdings grow (see `ONTOLOGY_GAPS.md` #4, #5, #10), should technical metrics like `frameRate`, `aspectRatio`, `width`/`height` (resolution), `bitDepth`, `bitRate`, `sampleRate`, and file `checksum` live directly on `fiaf:Item` (or a `fiaf:TechnicalCharacteristic` node), or on component track `Item`s?
5. **Migration Impact on Existing Transforms**:
   * `example/Carrier.ttl` and `example/Item.ttl` are trivial to update.
   * In `transform/bundesarchiv/xsl/bundesarchiv.xsl`, `ba:Aufbewahrungseinheit` currently maps to `fiaf:Carrier` via `fiaf:hasCarrier`, and puts both `DigitalFormat` and `DataStorageFormat` (`LTO2`–`LTO6`, `HardDrive`, `MagnetoOpticalDisc`) on `Item`. Separating the file `Item` from the storage carrier via `isPartOf`/`hasPart` would cleanly untangle those two `hasFormat` blocks in `bundesarchiv.xsl`.
