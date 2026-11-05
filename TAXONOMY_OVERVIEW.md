# How the Updated FIAFcore Taxonomies Interact

## 1. Division of Responsibilities

Each technical property on a `fiaf:Manifestation` or `fiaf:Item` answers one orthogonal question about the moving image embodiment or physical/digital artefact:

| Facet | Property & Target Class | Question Answered |
| :--- | :--- | :--- |
| **Format** | `fiaf:hasFormat` *(Manifestation, Item, Carrier)* → `fiaf:Format` | **What physical medium, digital file format, or package fixes it?** (`FilmFormat`, `AudioFormat`, `VideoFormat`, `DataStorageFormat`, `DigitalFormat`) |
| **Digital streams** | `fiaf:hasStream` *(Item, Carrier)* → `fiaf:DigitalStream` | **Which internal video, audio, or subtitle streams are described?** Codecs, language usage, and colour/sound characteristics are grouped per stream. |
| **Element** *(Item only)* | `fiaf:isElement` → `fiaf:Element` | **What is this artefact's functional role or generation in the workflow, including film polarity?** (`FilmElement` → `Negative` / `Positive`; `AudioElement`, `VideoElement`, `DigitalElement`) |
| **Colour** | `fiaf:hasColourCharacteristic` → `fiaf:ColourCharacteristic` (`BlackAndWhite`, `Colour`) | **Is it monochrome or colour, and how is colour produced or digitally encoded on this artefact?**<ul><li>Film: `fiaf:hasColourProcess` → `fiaf:ColourStandard`</li><li>Digital: `fiaf:hasColourEncoding` → `fiaf:ColourEncoding`<br>`fiaf:hasColourSpace` → `fiaf:ColourSpace`<br>`fiaf:hasTransferFunction` → `fiaf:TransferFunction`</li></ul> |
| **Sound** | `fiaf:hasSoundCharacteristic` → `fiaf:SoundCharacteristic` (`Silent`, `Mute`, `Sound`) | **Is sound present, and by what process/system, noise reduction, and channel layout is it fixed?**<ul><li>`fiaf:hasSoundStandard` → `fiaf:SoundStandard`</li><li>`fiaf:hasNoiseReduction` → `fiaf:NoiseReduction`</li><li>`fiaf:hasSoundChannelConfiguration` → `fiaf:SoundChannelConfiguration`</li></ul> |

`fiaf:hasColourStandard` is retained only as a deprecated alias of `fiaf:hasColourProcess`; new data should use `fiaf:hasColourProcess`.

### Core Design Principles
1. **Describe the artefact itself at the `Item` level**:
   - **Applied colour (`Tinted`, `Toned`, `HandColouring`, `StencilColouring`)**: A tinted nitrate print has `fiaf:hasColourCharacteristic [ fiaf:hasColourProcess fiaf:Tinted ]` (`fiaf:BlackAndWhite` is used only when the film is actually black and white in appearance, or also contains untinted black-and-white sequences; `fiaf:Colour` is reserved for natural/mimetic colour).
   - **Digital scans of photochemical prints**: A digital preservation scan of that tinted print describes its digital pixel representation (`[ fiaf:hasColourEncoding fiaf:RGB ; fiaf:hasColourSpace fiaf:ACES2065_1 ; fiaf:hasTransferFunction fiaf:Linear ]`, omitting both `BlackAndWhite` and `Colour` just as on the tinted source print), never photochemical tinting (`hasColourProcess`). ACES2065-1 is an illustrative choice, not a format inferred for every scan.
   - **Colour separation elements & dye-transfer matrices**: Single-channel (or sequential-frame) separation negatives (`fiaf:ColourSeparationNegative`), separation positives/protection masters (`fiaf:ColourSeparationPositive`), and Technicolor relief matrices (`fiaf:DyeTransferMatrix`) are monochrome intermediate elements, not colour prints. They are identified via `fiaf:isElement` (under `fiaf:Negative` and `fiaf:Positive`) and carry `fiaf:hasColourCharacteristic [ a fiaf:BlackAndWhite ]` without a `hasColourProcess`.
2. **Symmetric `ColourCharacteristic` and `SoundCharacteristic` blank nodes**: Both Colour and Sound use a qualifying blank node so multiple characteristics on the same Manifestation/Item (e.g., B&W + Technicolor sequences, B&W + Tinted sequences, or several soundtracks) stay cleanly grouped. Each `SoundCharacteristic` node describes **one soundtrack**; a 35mm quad-track print (SDDS + Dolby Digital + Dolby Stereo SR + DTS) therefore carries four nodes, one per track.
3. **Functional modality across `Format` and `Element`**:
   - Perforated film gauges (`35mmFilm`, `35mmMagneticFilm`) live under `FilmFormat`, while all separated sound-only elements (`SoundNegative`, `SoundPositive`, `SeparatedMagneticSound`, `AudioMaster`) live under `AudioElement`.
   - **Film polarity stays in `Element`**: `Negative` and `Positive` are the organising division of `FilmElement` because in photochemical duplication polarity *is* function — camera originals are negative (except reversal originals), protection masters are positive (`DuplicatePositive`, `ColourSeparationPositive`), printing masters are negative (`DuplicateNegative`, `ColourReversalIntermediate`), and editorial/grading/exhibition prints are positive (`WorkPrint`, `AnswerPrint`, `ReleasePrint`). `FilmFormat` stays orthogonal: it records the gauge, never the polarity.
   - **Magnetic sound is split across four layers**: `hasFormat fiaf:35mmMagneticFilm` (gauge/material), `hasSoundStandard fiaf:Magnetic` (recording process and track layout), `hasNoiseReduction fiaf:DolbyA` / `fiaf:DolbySR` (companding, where known), and `isElement fiaf:SeparatedMagneticSound` (a sound-only element carried separately from the image, distinct from `AudioMaster`, `SoundNegative`, and `SoundPositive`).
   - Optical discs are placed by functional modality rather than laser physics: authored video discs (`DVD`, `BluRay`, `UltraHDBluRay`, `LaserDisc`, `VCD`, `SVCD`) sit under `fiaf:VideoFormat` → `fiaf:OpticalVideoDisc` (aligning with `fiaf:VideoElement` such as `HomeViewingCopy` and `VideoAccessCopy`); audio compact discs (`CD`) sit under `fiaf:AudioFormat`; and recordable data discs (`CDR`, `DVDR`) sit under `fiaf:DataStorageFormat`.
4. **Digital objects and storage media describe separate objects**: Keep `DigitalFormat` (container, image file, package) on the digital object and `DataStorageFormat` on its storage unit where possible. Item-level and Carrier-level stream descriptions are equally valid; archives need not introduce an entity below Item. `hasStream` groups optional internal streams with their codecs, language usage, and characteristics. A stream is not an inventory holding; a multichannel audio stream is not one stream per channel. Film continues to use ordinary format and characteristic descriptions without a mandatory track model. Storage/content and package-component relationships, and the meaning of Carrier itself, remain open in `TAXONOMY_REVIEW.md` §4.8. See `FORMAT_TAXONOMY.md` for rationale, migration limits, and examples.

---

## 2. Taxonomy Trees

The trees below describe the updated `ontology/*.ttl` hierarchies, including optional digital streams and the independent codec trees. `Carrier` and `Manifestation` have no subclass changes shown here. Carrier's definition remains under review rather than being settled by the stream additions.

### 2.1 Format

`fiaf:hasFormat` targets `fiaf:Format`. On this branch, `28mmFilm` and the expanded `VideoFormat`, `DataStorageFormat`, and `DigitalFormat` branches were added; `16mmMagneticFilm` and `35mmMagneticFilm` moved from `AudioFormat` to `FilmFormat`; and `OpticalFormat` was dissolved.

```text
fiaf:Format
│
├── fiaf:FilmFormat
│   ├── fiaf:8mmFilm
│   ├── fiaf:9.5mmFilm
│   ├── fiaf:16mmFilm
│   ├── fiaf:16mmMagneticFilm
│   ├── fiaf:17.5mmFilm
│   ├── fiaf:28mmFilm
│   ├── fiaf:35mmFilm
│   ├── fiaf:35mmMagneticFilm
│   ├── fiaf:70mmFilm
│   ├── fiaf:Super8mmFilm
│   └── fiaf:Super16mmFilm
│
├── fiaf:AudioFormat
│   ├── fiaf:Audiocassette
│   ├── fiaf:CD
│   ├── fiaf:DAT
│   ├── fiaf:DTRS
│   ├── fiaf:HalfInchAudiotape
│   ├── fiaf:OneInchAudiotape
│   ├── fiaf:QuerterInchAudiotape
│   └── fiaf:TwoInchAudiotape
│
├── fiaf:VideoFormat
│   ├── fiaf:Betacam
│   │   ├── fiaf:BetacamSP
│   │   └── fiaf:DigitalBetacam
│   ├── fiaf:Betamax
│   ├── fiaf:D1
│   ├── fiaf:D2
│   ├── fiaf:D3
│   ├── fiaf:D5
│   ├── fiaf:D6
│   ├── fiaf:DV
│   │   ├── fiaf:DVCAM
│   │   ├── fiaf:DVCPRO
│   │   │   └── fiaf:DVCPROHD
│   │   └── fiaf:MiniDV
│   ├── fiaf:HalfInchVideotape
│   ├── fiaf:HDCAM
│   ├── fiaf:HDCAMSR
│   ├── fiaf:HDV
│   ├── fiaf:OneInchVideotape
│   │   ├── fiaf:OneInchTypeA
│   │   ├── fiaf:OneInchTypeB
│   │   └── fiaf:OneInchTypeC
│   ├── fiaf:OpticalVideoDisc
│   │   ├── fiaf:BluRay
│   │   │   └── fiaf:UltraHDBluRay
│   │   ├── fiaf:DVD
│   │   ├── fiaf:LaserDisc
│   │   ├── fiaf:SVCD
│   │   └── fiaf:VCD
│   ├── fiaf:TwoInchVideotape
│   ├── fiaf:Umatic
│   │   ├── fiaf:UmaticHighBand
│   │   ├── fiaf:UmaticLowBand
│   │   └── fiaf:UmaticSP
│   ├── fiaf:VCR
│   ├── fiaf:VHS
│   │   └── fiaf:SuperVHS
│   ├── fiaf:Video2000
│   └── fiaf:Video8
│       └── fiaf:Hi8
│
├── fiaf:DataStorageFormat
│   ├── fiaf:CDR
│   ├── fiaf:DVDR
│   ├── fiaf:FlashMemory
│   ├── fiaf:HardDrive
│   ├── fiaf:LTO
│   │   ├── fiaf:LTO2
│   │   ├── fiaf:LTO3
│   │   ├── fiaf:LTO4
│   │   ├── fiaf:LTO5
│   │   └── fiaf:LTO6
│   └── fiaf:MagnetoOpticalDisc
│
└── fiaf:DigitalFormat
    ├── fiaf:ContainerFormat
    │   ├── fiaf:AVI
    │   ├── fiaf:MKV
    │   ├── fiaf:MOV
    │   ├── fiaf:MP4
    │   ├── fiaf:MXF
    │   ├── fiaf:Quicktime
    │   ├── fiaf:VOB
    │   ├── fiaf:WAV
    │   └── fiaf:WebM
    ├── fiaf:ImageFormat
    │   ├── fiaf:Cineon
    │   ├── fiaf:DPX
    │   ├── fiaf:OpenEXR
    │   └── fiaf:TIFF
    └── fiaf:PackageFormat
        ├── fiaf:DCDM
        ├── fiaf:DCP
        └── fiaf:IMF

fiaf:DigitalStream                         via hasStream on Item ∪ Carrier
├── fiaf:VideoStream                        hasVideoCodec; hasColourCharacteristic
├── fiaf:AudioStream                        hasAudioCodec; hasSoundCharacteristic
└── fiaf:SubtitleStream
                                           all streams: hasLanguageUsage

fiaf:VideoCodec
├── fiaf:FFV1
├── fiaf:MPEG2
├── fiaf:MPEG-4
├── fiaf:ProRes
│   └── fiaf:ProRes422HQ
├── fiaf:RealVideo
└── fiaf:WindowsMedia

fiaf:AudioCodec
└── fiaf:PCM
```

### 2.2 Element

On this branch, the `FilmElement`, `AudioElement`, `VideoElement`, and `DigitalElement` branches were added. `Negative` and `Positive` sit under `FilmElement`, with the colour separation, dye-transfer matrix, and intermediate classes nested beneath them. This is deliberate: `Element` describes an artefact's role in the workflow *including* its photochemical polarity (see §1, Principle 3), while `Format` describes its physical medium, file format, or package. Codecs describe digital streams separately. `AudioElement`, `VideoElement`, and `DigitalElement` carry no polarity, since polarity is a photochemical concept.

```text
fiaf:Element
├── fiaf:AudioElement
│   ├── fiaf:AudioMaster
│   ├── fiaf:SeparatedMagneticSound
│   ├── fiaf:SoundNegative
│   └── fiaf:SoundPositive
├── fiaf:DigitalElement
│   ├── fiaf:DigitalAccessCopy
│   ├── fiaf:DigitalMaster
│   └── fiaf:DigitalMezzanine
├── fiaf:FilmElement
│   ├── fiaf:Negative
│   │   ├── fiaf:ColourSeparationNegative
│   │   ├── fiaf:DuplicateNegative
│   │   │   └── fiaf:ColourReversalIntermediate
│   │   └── fiaf:OriginalNegative
│   └── fiaf:Positive
│       ├── fiaf:AnswerPrint
│       ├── fiaf:ColourSeparationPositive
│       ├── fiaf:DuplicatePositive
│       ├── fiaf:DyeTransferMatrix
│       ├── fiaf:ReleasePrint
│       ├── fiaf:ReversalPositive
│       └── fiaf:WorkPrint
└── fiaf:VideoElement
    ├── fiaf:HomeViewingCopy
    ├── fiaf:OriginalVideoRecording
    ├── fiaf:VideoAccessCopy
    └── fiaf:VideoMaster
```

### 2.3 Colour

`fiaf:hasColourCharacteristic` targets `fiaf:ColourCharacteristic`, which carries the appearance-level `BlackAndWhite`/`Colour` distinction. `fiaf:hasColourProcess` (formerly `hasColourStandard`) targets the photochemical `ColourStandard` tree; digital colour properties use `ColourEncoding`, `ColourSpace`, and `TransferFunction`.

On this branch, `ColourStandard` was expanded and restructured; `ColourEncoding`, `ColourSpace`, `TransferFunction`, and their properties were added; and `Tinted`, `Toned`, `HandColouring`, and `StencilColouring` moved under `AppliedColourProcess`.

```text
fiaf:ColourCharacteristic
├── fiaf:BlackAndWhite
└── fiaf:Colour

fiaf:ColourStandard
├── fiaf:AppliedColourProcess
│   ├── fiaf:HandColouring
│   ├── fiaf:StencilColouring
│   │   └── fiaf:Pathecolor
│   ├── fiaf:Tinted
│   └── fiaf:Toned
└── fiaf:MimeticColourProcess
    ├── fiaf:AdditiveColourProcess
    │   ├── fiaf:ScreenProcess
    │   │   ├── fiaf:LenticularScreen
    │   │   │   └── fiaf:Kodacolor
    │   │   ├── fiaf:LineScreen
    │   │   └── fiaf:MosaicScreen
    │   │       └── fiaf:Dufaycolor
    │   ├── fiaf:SpatialSynthesis
    │   └── fiaf:TemporalSynthesis
    │       └── fiaf:Kinemacolor
    └── fiaf:SubtractiveColourProcess
        ├── fiaf:ChromogenicMonopack
        │   ├── fiaf:Agfacolor
        │   ├── fiaf:Anscocolor
        │   ├── fiaf:DeLuxe
        │   ├── fiaf:Duartcolor
        │   ├── fiaf:Eastmancolor
        │   ├── fiaf:Ektachrome
        │   ├── fiaf:Ferraniacolor
        │   ├── fiaf:Fujicolor
        │   ├── fiaf:Gevacolor
        │   ├── fiaf:Kodachrome
        │   ├── fiaf:Metrocolor
        │   ├── fiaf:Orwocolor
        │   ├── fiaf:Sovcolor
        │   └── fiaf:Warnercolor
        ├── fiaf:ChromolyticMultilayer
        │   └── fiaf:Gasparcolor
        ├── fiaf:ChromolyticSingleLayer
        ├── fiaf:ColourSeparation
        │   └── fiaf:Supercinecolor
        ├── fiaf:DirectPositive
        ├── fiaf:DoubleCoatedBipack
        │   ├── fiaf:Cinecolor
        │   ├── fiaf:Trucolor
        │   └── fiaf:Ufacolor
        ├── fiaf:InstantDyeDiffusion
        └── fiaf:PrintingDyeTransferPigment
            └── fiaf:Technicolor
```

```text
fiaf:ColourEncoding
├── fiaf:Greyscale
├── fiaf:RGB
├── fiaf:XYZ
└── fiaf:YUV

fiaf:ColourSpace
├── fiaf:ACES2065_1                         ACES2065-1 (AP0), scene-linear RGB
├── fiaf:DCIP3
├── fiaf:Rec601
├── fiaf:Rec709
├── fiaf:Rec2020
└── fiaf:sRGB

fiaf:TransferFunction
├── fiaf:Gamma
├── fiaf:HLG
├── fiaf:Linear
├── fiaf:Logarithmic
└── fiaf:PQ
```

### 2.4 Sound

`fiaf:hasSoundCharacteristic` targets `fiaf:SoundCharacteristic`; `fiaf:hasSoundStandard` targets `fiaf:SoundStandard`; `fiaf:hasNoiseReduction` targets `fiaf:NoiseReduction`; and `fiaf:hasSoundChannelConfiguration` targets `fiaf:SoundChannelConfiguration`. `SoundStandard` now covers only the fixation process or playback/encoding system; noise reduction is its own homogeneous tree. `SDDS` moved under `DigitalSoundSystem`, alongside `DolbyDigital` and `DTS`. Each `SoundCharacteristic` node describes one soundtrack. See `SOUND_TAXONOMY.md` §5 for the design rationale.

```text
fiaf:SoundCharacteristic
├── fiaf:Mute
├── fiaf:Silent
└── fiaf:Sound

fiaf:SoundStandard
├── fiaf:DigitalSoundSystem
│   ├── fiaf:DTS
│   │   └── fiaf:DTSHD
│   ├── fiaf:Datasat
│   ├── fiaf:DolbyAtmos
│   ├── fiaf:DolbyDigital
│   │   ├── fiaf:DolbyDigitalPlus
│   │   └── fiaf:DolbyDigitalSurroundEX
│   ├── fiaf:DolbyTrueHD
│   └── fiaf:SDDS
├── fiaf:Magnetic
│   ├── fiaf:FourTrackMagnetic
│   └── fiaf:SixTrackMagnetic
└── fiaf:OpticalSoundProcess
    ├── fiaf:OpticalVariableArea
    │   ├── fiaf:DolbyStereo
    │   └── fiaf:UltraStereo
    └── fiaf:OpticalVariableDensity

fiaf:NoiseReduction
└── fiaf:Dolby
    ├── fiaf:DolbyA
    └── fiaf:DolbySR

fiaf:SoundChannelConfiguration
├── fiaf:Mono
├── fiaf:Stereo
└── fiaf:Surround
```

### 2.5 Language

`fiaf:Language` remains a flat ISO 639 list. The six classes added on this branch are `Bodo`, `BritishSignLanguage`, `LowerSorbian`, `Rajasthani`, `SouthernSami`, and `UpperSorbian`.

```text
fiaf:Language
├── fiaf:Abkhazian
├── fiaf:Afar
├── fiaf:Afrikaans
├── fiaf:Akan
├── fiaf:Albanian
├── fiaf:Amharic
├── fiaf:Arabic
├── fiaf:Aragonese
├── fiaf:Armenian
├── fiaf:Assamese
├── fiaf:Avaric
├── fiaf:Avestan
├── fiaf:Aymara
├── fiaf:Azerbaijani
├── fiaf:Bambara
├── fiaf:Bashkir
├── fiaf:Basque
├── fiaf:Belarusian
├── fiaf:Bengali
├── fiaf:Bislama
├── fiaf:Bodo
├── fiaf:Bosnian
├── fiaf:Breton
├── fiaf:BritishSignLanguage
├── fiaf:Bulgarian
├── fiaf:Burmese
├── fiaf:Catalan
├── fiaf:CentralKhmer
├── fiaf:Chamorro
├── fiaf:Chechen
├── fiaf:Chichewa
├── fiaf:Chinese
├── fiaf:ChurchSlavonic
├── fiaf:Chuvash
├── fiaf:Cornish
├── fiaf:Corsican
├── fiaf:Cree
├── fiaf:Croatian
├── fiaf:Czech
├── fiaf:Danish
├── fiaf:Divehi
├── fiaf:Dutch
├── fiaf:Dzongkha
├── fiaf:English
├── fiaf:Esperanto
├── fiaf:Estonian
├── fiaf:Ewe
├── fiaf:Faroese
├── fiaf:Fijian
├── fiaf:Finnish
├── fiaf:French
├── fiaf:Fulah
├── fiaf:Gaelic
├── fiaf:Galician
├── fiaf:Ganda
├── fiaf:Georgian
├── fiaf:German
├── fiaf:Greek
├── fiaf:Guarani
├── fiaf:Gujarati
├── fiaf:Haitian
├── fiaf:Hausa
├── fiaf:Hawaiian
├── fiaf:Hebrew
├── fiaf:Herero
├── fiaf:Hindi
├── fiaf:HiriMotu
├── fiaf:Hungarian
├── fiaf:Icelandic
├── fiaf:Ido
├── fiaf:Igbo
├── fiaf:Indonesian
├── fiaf:Interlingua
├── fiaf:Interlingue
├── fiaf:Inuktitut
├── fiaf:Inupiaq
├── fiaf:Irish
├── fiaf:Italian
├── fiaf:Japanese
├── fiaf:Javanese
├── fiaf:Kalaallisut
├── fiaf:Kannada
├── fiaf:Kanuri
├── fiaf:Kashmiri
├── fiaf:Kazakh
├── fiaf:Kikuyu
├── fiaf:Kinyarwanda
├── fiaf:Komi
├── fiaf:Kongo
├── fiaf:Korean
├── fiaf:Kuanyama
├── fiaf:Kurdish
├── fiaf:Kyrgyz
├── fiaf:Lao
├── fiaf:Latin
├── fiaf:Latvian
├── fiaf:Limburgan
├── fiaf:Lingala
├── fiaf:Lithuanian
├── fiaf:LowerSorbian
├── fiaf:Lubakatanga
├── fiaf:Luxembourgish
├── fiaf:Macedonian
├── fiaf:Malagasy
├── fiaf:Malay
├── fiaf:Malayalam
├── fiaf:Maltese
├── fiaf:Manx
├── fiaf:Maori
├── fiaf:Marathi
├── fiaf:Marshallese
├── fiaf:Mongolian
├── fiaf:Nauru
├── fiaf:Navajo
├── fiaf:Ndonga
├── fiaf:Nepali
├── fiaf:NorthNdebele
├── fiaf:NorthernSami
├── fiaf:Norwegian
├── fiaf:NorwegianBokmal
├── fiaf:NorwegianNynorsk
├── fiaf:Occitan
├── fiaf:Ojibwa
├── fiaf:Oriya
├── fiaf:Oromo
├── fiaf:Ossetian
├── fiaf:Pali
├── fiaf:Pashto
├── fiaf:Persian
├── fiaf:Polish
├── fiaf:Portuguese
├── fiaf:Punjabi
├── fiaf:Quechua
├── fiaf:Rajasthani
├── fiaf:Romanian
├── fiaf:Romansh
├── fiaf:Rundi
├── fiaf:Russian
├── fiaf:Samoan
├── fiaf:Sango
├── fiaf:Sanskrit
├── fiaf:Sardinian
├── fiaf:Serbian
├── fiaf:Shona
├── fiaf:SichuanYi
├── fiaf:Sindhi
├── fiaf:Sinhala
├── fiaf:Slovak
├── fiaf:Slovenian
├── fiaf:Somali
├── fiaf:SouthNdebele
├── fiaf:SouthernSami
├── fiaf:SouthernSotho
├── fiaf:Spanish
├── fiaf:Sundanese
├── fiaf:Swahili
├── fiaf:Swati
├── fiaf:Swedish
├── fiaf:Tagalog
├── fiaf:Tahitian
├── fiaf:Tajik
├── fiaf:Tamil
├── fiaf:Tatar
├── fiaf:Telugu
├── fiaf:Thai
├── fiaf:Tibetan
├── fiaf:Tigrinya
├── fiaf:Tonga
├── fiaf:Tsonga
├── fiaf:Tswana
├── fiaf:Turkish
├── fiaf:Turkmen
├── fiaf:Twi
├── fiaf:Uighur
├── fiaf:Ukrainian
├── fiaf:UpperSorbian
├── fiaf:Urdu
├── fiaf:Uzbek
├── fiaf:Venda
├── fiaf:Vietnamese
├── fiaf:Volapuk
├── fiaf:Walloon
├── fiaf:Welsh
├── fiaf:WesternFrisian
├── fiaf:Wolof
├── fiaf:Xhosa
├── fiaf:Yiddish
├── fiaf:Yoruba
├── fiaf:Zhuang
└── fiaf:Zulu
```

## 3. Examples Across Media & Workflow Types

```turtle
@prefix fiaf: <https://dev.fiafcore.org/> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
```

### Example 1: Silent Tinted Nitrate Print & Its Digital Preservation Scan
A 35mm nitrate release print of a silent film with tinted images, alongside a 4K RGB DPX preservation scan made from that print (neither asserts `fiaf:BlackAndWhite` or `fiaf:Colour`, and the scan carries only digital colour properties):

```turtle
# 1a. Photochemical Tinted Nitrate Print
<https://example.fiafcore.org/item/silent-nitrate-print>
    a fiaf:Item ;
    rdfs:label "35mm Tinted Nitrate Release Print"@en ;
    fiaf:hasBase fiaf:NitrateBase ;
    fiaf:hasFormat fiaf:35mmFilm ;
    fiaf:isElement fiaf:ReleasePrint ;                  # Positive -> FilmElement
    fiaf:hasStatus fiaf:Preservation ;
    fiaf:hasColourCharacteristic [
        fiaf:hasColourProcess fiaf:Tinted               # AppliedColourProcess -> ColourStandard
    ] ;
    fiaf:hasSoundCharacteristic [
        a fiaf:Silent
    ] .

# 1b. Digital Preservation Scan of the Tinted Print (with per-reel DPX Carriers)
<https://example.fiafcore.org/item/scan-of-tinted-print>
    a fiaf:Item ;
    rdfs:label "DPX Digital Preservation Scan of Tinted Nitrate Print"@en ;
    fiaf:hasFormat fiaf:DPX ;                           # ImageFormat -> DigitalFormat
    fiaf:isElement fiaf:DigitalMaster ;                 # DigitalElement
    fiaf:hasStatus fiaf:Preservation ;
    fiaf:hasColourCharacteristic [
        fiaf:hasColourEncoding fiaf:RGB ;               # Digital encoding only; no hasColourProcess
        fiaf:hasColourSpace fiaf:ACES2065_1 ;
        fiaf:hasTransferFunction fiaf:Linear
    ] ;
    fiaf:hasSoundCharacteristic [
        a fiaf:Silent
    ] ;
    fiaf:hasCarrier <https://example.fiafcore.org/carrier/dpx-reel-1>,
                    <https://example.fiafcore.org/carrier/dpx-reel-2> .

<https://example.fiafcore.org/carrier/dpx-reel-1>
    a fiaf:Carrier ;
    rdfs:label "Reel 1 DPX Sequence"@en ;
    fiaf:hasFormat fiaf:DPX .
```

### Example 2: 1990s Theatrical Manifestation & 35mm Release Print with Dual Optical Soundtracks
A theatrical release print on Eastmancolor stock carrying both a Dolby Digital (SRD) 5.1 surround track and an analogue Dolby Stereo SR optical variable-area backup track:

```turtle
<https://example.fiafcore.org/manifestation/theatrical-1995>
    a fiaf:TheatricalManifestation ;
    rdfs:label "1995 Theatrical Release"@en ;
    fiaf:hasFormat fiaf:35mmFilm ;
    fiaf:hasColourCharacteristic [
        a fiaf:Colour ;
        fiaf:hasColourProcess fiaf:Eastmancolor         # ChromogenicMonopack -> SubtractiveColourProcess
    ] ;
    fiaf:hasSoundCharacteristic
        [ a fiaf:Sound ;
          fiaf:hasSoundStandard fiaf:DolbyDigital ;     # DigitalSoundSystem
          fiaf:hasSoundChannelConfiguration fiaf:Surround ],
        [ a fiaf:Sound ;
          fiaf:hasSoundStandard fiaf:DolbyStereo ;       # OpticalVariableArea -> OpticalSoundProcess
          fiaf:hasNoiseReduction fiaf:DolbySR ;          # NoiseReduction
          fiaf:hasSoundChannelConfiguration fiaf:Stereo ] ;
    fiaf:hasItem <https://example.fiafcore.org/item/print-1995> .

<https://example.fiafcore.org/item/print-1995>
    a fiaf:Item ;
    rdfs:label "35mm Combined Release Print"@en ;
    fiaf:hasBase fiaf:PolyesterBase ;
    fiaf:hasFormat fiaf:35mmFilm ;
    fiaf:isElement fiaf:ReleasePrint ;
    fiaf:hasStatus fiaf:Access ;
    fiaf:hasColourCharacteristic [
        a fiaf:Colour ;
        fiaf:hasColourProcess fiaf:Eastmancolor
    ] ;
    fiaf:hasSoundCharacteristic
        [ a fiaf:Sound ;
          fiaf:hasSoundStandard fiaf:DolbyDigital ;
          fiaf:hasSoundChannelConfiguration fiaf:Surround ],
        [ a fiaf:Sound ;
          fiaf:hasSoundStandard fiaf:DolbyStereo ;
          fiaf:hasNoiseReduction fiaf:DolbySR ;
          fiaf:hasSoundChannelConfiguration fiaf:Stereo ] .
```

### Example 3: Hybrid Colour Film (*Sepia-Toned + Three-Strip Technicolor*) & Colour Separation / Matrix Elements
An Item containing both sepia-toned sequences and three-strip Technicolor sequences, alongside a monochrome YCM colour separation protection master (`ColourSeparationPositive`) and a Technicolor dye-transfer printing matrix (`DyeTransferMatrix`):

```turtle
<https://example.fiafcore.org/item/hybrid-colour-print>
    a fiaf:Item ;
    rdfs:label "35mm Hybrid Sepia and Technicolor Print"@en ;
    fiaf:hasFormat fiaf:35mmFilm ;
    fiaf:isElement fiaf:ReleasePrint ;
    fiaf:hasColourCharacteristic
        [ fiaf:hasColourProcess fiaf:Toned ],           # AppliedColourProcess
        [ a fiaf:Colour ;
          fiaf:hasColourProcess fiaf:Technicolor ] .    # PrintingDyeTransferPigment -> SubtractiveColourProcess

# Cyan Separation Protection Master ("Promaster"): monochrome B&W positive element
<https://example.fiafcore.org/item/cyan-separation-promaster>
    a fiaf:Item ;
    rdfs:label "35mm Cyan Separation Promaster"@en ;
    fiaf:hasBase fiaf:AcetateBase ;
    fiaf:hasFormat fiaf:35mmFilm ;
    fiaf:isElement fiaf:ColourSeparationPositive ;      # Positive -> FilmElement
    fiaf:hasStatus fiaf:Preservation ;
    fiaf:hasColourCharacteristic [
        a fiaf:BlackAndWhite
    ] ;
    fiaf:hasSoundCharacteristic [
        a fiaf:Mute
    ] .

# Technicolor Dye-Transfer Matrix: monochrome relief printing element
<https://example.fiafcore.org/item/cyan-matrix>
    a fiaf:Item ;
    rdfs:label "35mm Cyan Separation Matrix"@en ;
    fiaf:hasFormat fiaf:35mmFilm ;
    fiaf:isElement fiaf:DyeTransferMatrix ;             # Positive -> FilmElement
    fiaf:hasStatus fiaf:Preservation ;
    fiaf:hasColourCharacteristic [
        a fiaf:BlackAndWhite
    ] .
```

### Example 4: Separated Sound Followers (`Sepmag` and `Sepopt`)
Both live under `fiaf:AudioElement` (so querying `AudioElement` finds all sound-only elements) and under `fiaf:FilmFormat` (so querying `FilmFormat` finds all perforated film items):

```turtle
# 35mm Separated Magnetic Sound Follower (Sepmag)
<https://example.fiafcore.org/item/sepmag-follower>
    a fiaf:Item ;
    rdfs:label "35mm 4-Track Sepmag Master"@en ;
    fiaf:hasBase fiaf:AcetateBase ;
    fiaf:hasFormat fiaf:35mmMagneticFilm ;              # FilmFormat
    fiaf:isElement fiaf:SeparatedMagneticSound ;        # AudioElement
    fiaf:hasStatus fiaf:Preservation ;
    fiaf:hasSoundCharacteristic [
        a fiaf:Sound ;
        fiaf:hasSoundStandard fiaf:FourTrackMagnetic ;
        fiaf:hasNoiseReduction fiaf:DolbyA ;
        fiaf:hasSoundChannelConfiguration fiaf:Surround
    ] .

# 35mm Optical Sound Negative (Sepopt)
<https://example.fiafcore.org/item/optical-sound-neg>
    a fiaf:Item ;
    rdfs:label "35mm Optical Sound Negative"@en ;
    fiaf:hasBase fiaf:PolyesterBase ;
    fiaf:hasFormat fiaf:35mmFilm ;                      # FilmFormat
    fiaf:isElement fiaf:SoundNegative ;                 # AudioElement
    fiaf:hasStatus fiaf:Preservation ;
    fiaf:hasSoundCharacteristic [
        a fiaf:Sound ;
        fiaf:hasSoundStandard fiaf:OpticalVariableArea ;
        fiaf:hasSoundChannelConfiguration fiaf:Mono
    ] .
```

### Example 5: Broadcast Video Master, VHS Home Video, & Authored DVD-Video Disc
A Digital Betacam PAL broadcast master, a consumer VHS home viewing copy, and an authored DVD-Video access disc (`OpticalVideoDisc` → `VideoFormat`):

```turtle
<https://example.fiafcore.org/item/digibeta-master>
    a fiaf:Item ;
    rdfs:label "Digital Betacam PAL Master"@en ;
    fiaf:hasBroadcastStandard fiaf:PAL ;
    fiaf:hasFormat fiaf:DigitalBetacam ;                # Betacam -> VideoFormat
    fiaf:isElement fiaf:VideoMaster ;                   # VideoElement
    fiaf:hasStatus fiaf:Preservation ;
    fiaf:hasColourCharacteristic [
        a fiaf:Colour ;
        fiaf:hasColourEncoding fiaf:YUV ;
        fiaf:hasColourSpace fiaf:Rec601 ;
        fiaf:hasTransferFunction fiaf:Gamma
    ] ;
    fiaf:hasSoundCharacteristic [
        a fiaf:Sound ;
        fiaf:hasSoundChannelConfiguration fiaf:Stereo
    ] .

<https://example.fiafcore.org/item/vhs-home-copy>
    a fiaf:Item ;
    rdfs:label "VHS Home Viewing Copy"@en ;
    fiaf:hasBroadcastStandard fiaf:PAL ;
    fiaf:hasFormat fiaf:VHS ;                           # VideoFormat
    fiaf:isElement fiaf:HomeViewingCopy ;               # VideoElement
    fiaf:hasStatus fiaf:Access .

<https://example.fiafcore.org/item/dvd-video-access>
    a fiaf:Item ;
    rdfs:label "DVD-Video Access Copy"@en ;
    fiaf:hasBroadcastStandard fiaf:PAL ;
    fiaf:hasFormat fiaf:DVD ;                           # OpticalVideoDisc -> VideoFormat
    fiaf:isElement fiaf:VideoAccessCopy ;               # VideoElement
    fiaf:hasStatus fiaf:Access .

# A separately described file on that disc, when catalogued.
<https://example.fiafcore.org/carrier/dvd-vob-file>
    a fiaf:Carrier ;
    fiaf:hasFormat fiaf:VOB .
# The disc/file relationship remains part of the Carrier review.
```

### Example 6: Digital Objects (`DigitalFormat`) & Offline Data Storage Carriers (`DataStorageFormat`)
Digital objects use `DigitalFormat` (container, image file, package); optional streams group codecs and stream-specific characteristics. Storage media should be described separately. Storage/content relationships remain under review and are not asserted below. For multiple audio streams and shared language-usage nodes, see `example/DigitalStream.ttl`.

```turtle
# 1. Digital Preservation Master (file-level digital Item)
<https://example.fiafcore.org/item/digital-preservation-master>
    a fiaf:Item ;
    rdfs:label "FFV1/MKV Digital Preservation Master"@en ;
    fiaf:hasFormat fiaf:MKV ;                           # ContainerFormat -> DigitalFormat
    fiaf:hasStream
        [ a fiaf:VideoStream ; fiaf:hasVideoCodec fiaf:FFV1 ;
          fiaf:hasColourCharacteristic [
              a fiaf:BlackAndWhite ;
              fiaf:hasColourEncoding fiaf:Greyscale ;
              fiaf:hasTransferFunction fiaf:Linear ] ],
        [ a fiaf:AudioStream ; fiaf:hasAudioCodec fiaf:PCM ;
          fiaf:hasSoundCharacteristic [ a fiaf:Sound ;
              fiaf:hasSoundChannelConfiguration fiaf:Mono ] ] ;
    fiaf:isElement fiaf:DigitalMaster ;                 # DigitalElement
    fiaf:hasStatus fiaf:Preservation .

# 2. Theatrical DCP Access Package (package-level digital Item)
<https://example.fiafcore.org/item/dcp-access>
    a fiaf:Item ;
    rdfs:label "Theatrical DCP Access Copy"@en ;
    fiaf:hasFormat fiaf:DCP ;                           # PackageFormat -> DigitalFormat
    fiaf:isElement fiaf:DigitalAccessCopy ;             # DigitalElement
    fiaf:hasStatus fiaf:Access ;
    fiaf:hasColourCharacteristic [
        a fiaf:Colour ;
        fiaf:hasColourEncoding fiaf:XYZ ;
        fiaf:hasColourSpace fiaf:DCIP3 ;
        fiaf:hasTransferFunction fiaf:Gamma
    ] ;
    fiaf:hasSoundCharacteristic [
        a fiaf:Sound ;
        fiaf:hasSoundStandard fiaf:DolbyAtmos ;
        fiaf:hasSoundChannelConfiguration fiaf:Surround
    ] .

# 3. Digital Access File and Separate Recordable Data DVD
<https://example.fiafcore.org/item/mp4-on-dvdr>
    a fiaf:Item ;
    rdfs:label "MP4 Access File on Data DVD-R"@en ;
    fiaf:hasFormat fiaf:MP4 ;                           # ContainerFormat -> DigitalFormat
    fiaf:isElement fiaf:DigitalAccessCopy ;             # DigitalElement
    fiaf:hasStatus fiaf:Access .

<https://example.fiafcore.org/carrier/data-dvdr>
    a fiaf:Carrier ;
    fiaf:hasFormat fiaf:DVDR .
# The storage/content link is deliberately deferred to the Carrier review.

# 4. Physical LTO-6 Data Tape (when catalogued without file-level format details)
<https://example.fiafcore.org/item/lto6-tape>
    a fiaf:Item ;
    rdfs:label "LTO-6 Preservation Data Tape"@en ;
    fiaf:hasFormat fiaf:LTO6 ;                          # LTO -> DataStorageFormat
    fiaf:hasStatus fiaf:Preservation .
```

### Example 7: Quad-Track 35mm Release Print (Four Soundtracks)

A 1990s 35mm print carrying four soundtracks side by side: SDDS on the outer edges, Dolby Digital (SRD) between the perforations, a Dolby Stereo SR bilateral variable-area analogue track, and a DTS timecode track. Each soundtrack is its own `SoundCharacteristic` node, so noise reduction and channel layout stay attached to the correct track:

```turtle
<https://example.fiafcore.org/item/35mm-quad-track-print>
    a fiaf:Item ;
    rdfs:label "35mm Quad-Track Release Print"@en ;
    fiaf:hasFormat fiaf:35mmFilm ;
    fiaf:isElement fiaf:ReleasePrint ;
    fiaf:hasStatus fiaf:Access ;
    fiaf:hasSoundCharacteristic
        # SDDS: digital optical edge tracks
        [ a fiaf:Sound ;
          fiaf:hasSoundStandard fiaf:SDDS ;
          fiaf:hasSoundChannelConfiguration fiaf:Surround ],

        # Dolby Digital (SRD): digital data blocks between the perforations
        [ a fiaf:Sound ;
          fiaf:hasSoundStandard fiaf:DolbyDigital ;
          fiaf:hasSoundChannelConfiguration fiaf:Surround ],

        # Analogue backup: bilateral variable-area, Dolby Stereo matrix + Dolby SR
        [ a fiaf:Sound ;
          fiaf:hasSoundStandard fiaf:DolbyStereo ;      # OpticalVariableArea -> OpticalSoundProcess
          fiaf:hasNoiseReduction fiaf:DolbySR ;
          fiaf:hasSoundChannelConfiguration fiaf:Stereo ],

        # DTS: optical timecode synchronised with CD-ROM
        [ a fiaf:Sound ;
          fiaf:hasSoundStandard fiaf:DTS ;
          fiaf:hasSoundChannelConfiguration fiaf:Surround ] .
```
