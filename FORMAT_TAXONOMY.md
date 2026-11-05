# FIAFcore Format Taxonomy and Optional Digital Streams

The five Format branches are retained. Codecs are independent trees attached to optional digital streams, not additional formats of the enclosing object. Item and Carrier are equally valid stream description points; no entity below Item is required. Carrier reassessment remains open in `TAXONOMY_REVIEW.md` §4.8.

Branch: `unified-taxonomy` (Format work originally developed on `restructure-format-taxonomy`, based on `expand-videoformat-subclasses`)

## Object Property

- `fiaf:hasFormat` (domain: `fiaf:Manifestation` ∪ `fiaf:Item` ∪ `fiaf:Carrier`) → `fiaf:Format`

## Class Hierarchy (Tree)

```text
fiaf:Format
│
├── fiaf:FilmFormat
│   ├── fiaf:8mmFilm
│   ├── fiaf:9.5mmFilm
│   ├── fiaf:16mmFilm
│   ├── fiaf:16mmMagneticFilm                           moved from AudioFormat
│   ├── fiaf:17.5mmFilm
│   ├── fiaf:28mmFilm                                   NEW
│   ├── fiaf:35mmFilm
│   ├── fiaf:35mmMagneticFilm                           moved from AudioFormat
│   ├── fiaf:70mmFilm
│   ├── fiaf:Super8mmFilm
│   └── fiaf:Super16mmFilm
│
├── fiaf:AudioFormat
│   ├── fiaf:Audiocassette
│   ├── fiaf:CD                                         moved from OpticalFormat
│   ├── fiaf:DAT                                        NEW
│   ├── fiaf:DTRS                                       NEW
│   ├── fiaf:HalfInchAudiotape                          (duplicate declaration removed)
│   ├── fiaf:OneInchAudiotape
│   ├── fiaf:QuerterInchAudiotape
│   └── fiaf:TwoInchAudiotape
│
├── fiaf:VideoFormat
│   ├── fiaf:Betacam                                     NEW
│   │   ├── fiaf:BetacamSP
│   │   └── fiaf:DigitalBetacam
│   ├── fiaf:Betamax
│   ├── fiaf:D1
│   ├── fiaf:D2
│   ├── fiaf:D3
│   ├── fiaf:D5
│   ├── fiaf:D6                                          NEW
│   ├── fiaf:DV                                          NEW
│   │   ├── fiaf:DVCAM
│   │   ├── fiaf:DVCPRO                                  NEW
│   │   │   └── fiaf:DVCPROHD
│   │   └── fiaf:MiniDV
│   ├── fiaf:HalfInchVideotape                           NEW
│   ├── fiaf:HDCAM
│   ├── fiaf:HDCAMSR
│   ├── fiaf:HDV                                         NEW
│   ├── fiaf:OneInchVideotape
│   │   ├── fiaf:OneInchTypeA
│   │   ├── fiaf:OneInchTypeB
│   │   └── fiaf:OneInchTypeC
│   ├── fiaf:OpticalVideoDisc                            NEW (replaces OpticalFormat for video)
│   │   ├── fiaf:BluRay
│   │   │   └── fiaf:UltraHDBluRay                       NEW
│   │   ├── fiaf:DVD
│   │   ├── fiaf:LaserDisc
│   │   ├── fiaf:SVCD                                    moved from DigitalFormat
│   │   └── fiaf:VCD                                     moved from DigitalFormat
│   ├── fiaf:TwoInchVideotape
│   ├── fiaf:Umatic
│   │   ├── fiaf:UmaticHighBand
│   │   ├── fiaf:UmaticLowBand
│   │   └── fiaf:UmaticSP
│   ├── fiaf:VCR
│   ├── fiaf:VHS
│   │   └── fiaf:SuperVHS                                re-parented
│   ├── fiaf:Video2000
│   └── fiaf:Video8
│       └── fiaf:Hi8                                     re-parented
│
├── fiaf:DataStorageFormat                               NEW branch
│   ├── fiaf:CDR                                         NEW
│   ├── fiaf:DVDR                                        NEW
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
    ├── fiaf:ContainerFormat                             NEW branch
    │   ├── fiaf:AVI
    │   ├── fiaf:MKV
    │   ├── fiaf:MOV
    │   ├── fiaf:MP4
    │   ├── fiaf:MXF
    │   ├── fiaf:Quicktime
    │   ├── fiaf:VOB
    │   ├── fiaf:WAV
    │   └── fiaf:WebM
    ├── fiaf:ImageFormat                                  NEW branch
    │   ├── fiaf:Cineon
    │   ├── fiaf:DPX
    │   ├── fiaf:OpenEXR
    │   └── fiaf:TIFF
    └── fiaf:PackageFormat
        ├── fiaf:DCDM
        ├── fiaf:DCP
        └── fiaf:IMF
```

## Class Hierarchy (Nested List)

- `fiaf:Format`
  - `fiaf:FilmFormat` — a film gauge on which a moving image is recorded photochemically
    - `fiaf:8mmFilm`, `fiaf:9.5mmFilm`, `fiaf:16mmFilm`, `fiaf:17.5mmFilm`
    - `fiaf:28mmFilm` — non-standard gauge used chiefly for early home and educational projection
    - `fiaf:35mmFilm`, `fiaf:70mmFilm`
    - `fiaf:Super8mmFilm`, `fiaf:Super16mmFilm`
  - `fiaf:AudioFormat` — a physical non-film audio carrier
    - `fiaf:Audiocassette`, `fiaf:CD`
    - `fiaf:DAT` — Digital Audio Tape, 3.81mm digital audio cassette
    - `fiaf:DTRS` — Digital Tape Recording System, eight-track modular multitrack tape
    - `fiaf:HalfInchAudiotape`, `fiaf:OneInchAudiotape`, `fiaf:QuerterInchAudiotape`, `fiaf:TwoInchAudiotape`
  - `fiaf:VideoFormat` — a physical videotape, videocassette, or optical video disc format
    - `fiaf:Betacam` — Betacam family
      - `fiaf:BetacamSP`, `fiaf:DigitalBetacam`
    - `fiaf:Betamax`, `fiaf:VCR`, `fiaf:Video2000`
    - `fiaf:D1`, `fiaf:D2`, `fiaf:D3`, `fiaf:D5`
    - `fiaf:D6` — uncompressed HD videocassette
    - `fiaf:DV` — DV family
      - `fiaf:DVCAM`, `fiaf:MiniDV`
      - `fiaf:DVCPRO`
        - `fiaf:DVCPROHD`
    - `fiaf:HalfInchVideotape` — 1/2" gauge of the Betamax/VHS/Video 2000 families
    - `fiaf:HDCAM`, `fiaf:HDCAMSR`, `fiaf:HDV`
    - `fiaf:OneInchVideotape`
      - `fiaf:OneInchTypeA`, `fiaf:OneInchTypeB`, `fiaf:OneInchTypeC`
    - `fiaf:OpticalVideoDisc` — an optical disc format carrying moving image video
      - `fiaf:BluRay`
        - `fiaf:UltraHDBluRay`
      - `fiaf:DVD`, `fiaf:LaserDisc`, `fiaf:SVCD`, `fiaf:VCD`
    - `fiaf:TwoInchVideotape`
    - `fiaf:Umatic`
      - `fiaf:UmaticHighBand`, `fiaf:UmaticLowBand`, `fiaf:UmaticSP`
    - `fiaf:VHS`
      - `fiaf:SuperVHS`
    - `fiaf:Video8`
      - `fiaf:Hi8`
  - `fiaf:DataStorageFormat` — an offline digital storage carrier
    - `fiaf:CDR`, `fiaf:DVDR`
    - `fiaf:LTO2`, `fiaf:LTO3`, `fiaf:LTO4`, `fiaf:LTO5`, `fiaf:LTO6`
    - `fiaf:HardDrive`, `fiaf:FlashMemory`, `fiaf:MagnetoOpticalDisc`
  - `fiaf:DigitalFormat` — a digital file container, image file format, or deliverable package
    - `fiaf:ContainerFormat` — a file container holding image/audio/metadata streams
      - `fiaf:AVI`, `fiaf:MKV`, `fiaf:MOV`, `fiaf:MP4`, `fiaf:MXF`
      - `fiaf:Quicktime`, `fiaf:VOB`, `fiaf:WAV`, `fiaf:WebM`
    - `fiaf:ImageFormat` — an image file format; image data may be compressed or uncompressed
      - `fiaf:Cineon`, `fiaf:DPX`, `fiaf:OpenEXR`, `fiaf:TIFF`
    - `fiaf:PackageFormat` — a defined deliverable bundle, not a single file
      - `fiaf:DCDM` — Digital Cinema Distribution Master, uncompressed (SMPTE ST 428)
      - `fiaf:DCP` — Digital Cinema Package (SMPTE / Interop)
      - `fiaf:IMF` — Interoperable Master Format (SMPTE ST 2067)

## Notes

- `fiaf:Format` is the root of its SKOS scheme. VideoCodec and AudioCodec have their own ontology files and generated schemes, preserving existing term IRIs without retaining codec subclass links to Format.
- `fiaf:MP4` (container) and `fiaf:MPEG-4` (codec) are now distinct classes in distinct
  branches, resolving the previous ambiguity where both were peers under `fiaf:DigitalFormat`.
- `fiaf:VCD` and `fiaf:SVCD` moved from `fiaf:DigitalFormat` to `fiaf:OpticalVideoDisc`
  under `fiaf:VideoFormat`, alongside `DVD` and `BluRay`; `fiaf:CD` remains an
  `AudioFormat`.
- `fiaf:DCDM`, `fiaf:DCP`, `fiaf:IMF`, `fiaf:FFV1`, `fiaf:PCM` and `fiaf:MKV` are deliberate
  additions without evidence in the NLN, BFI or Bundesarchiv datasets; remainder of the tree
  is grounded in observed source values.
- `fiaf:ContainerFormat` holds only true wrappers (`AVI`, `MKV`, `MOV`, `MP4`, `MXF`,
  `Quicktime`, `VOB`, `WAV`, `WebM`). `fiaf:DPX`, `fiaf:TIFF`, `fiaf:OpenEXR` and
  `fiaf:Cineon` sit under `fiaf:ImageFormat` instead. This is not a claim that image formats cannot use compression. Queries covering all
  digital files should use `rdfs:subClassOf* fiaf:DigitalFormat`.
- `fiaf:RealVideo` and `fiaf:WindowsMedia` were preserved and re-parented under
  `fiaf:VideoCodec`: they were declared on `develop` but appear in no dataset, and nothing
  references them. Removing them would be an IRI removal rather than a re-parenting, so it
  would be a breaking change for anyone outside the repo who already used them.
- Digital audio/video codecs are independent of Format and SoundStandard. See the stream model below.

## Digital streams and codec trees

```text
DigitalStream                         via hasStream on Item ∪ Carrier
├── VideoStream                       hasVideoCodec; hasColourCharacteristic
├── AudioStream                       hasAudioCodec; hasSoundCharacteristic
└── SubtitleStream
                                      all streams: hasLanguageUsage

VideoCodec                            via hasVideoCodec on VideoStream
├── FFV1
├── MPEG2
├── MPEG-4
├── ProRes
│   └── ProRes422HQ
├── RealVideo
└── WindowsMedia

AudioCodec                            via hasAudioCodec on AudioStream
└── PCM
```

### Rationale and boundaries

- A file format describes the enclosing digital object; a codec describes a stream's encoding. One container can contain many streams, including several with the same codec. A codec does not identify a stream.
- Stream nodes bind codec, language usage, and colour/sound characteristics without a cross-product between unrelated streams. They may be blank nodes or IRIs, and are not inventory Items or Carriers. One multichannel audio stream is not one stream per channel.
- This borrows the resource/track distinction from [EBUCore](https://github.com/ebu/ebucore/blob/master/ebucore.rdf), which has Track, AudioTrack, VideoTrack, and codec properties. It does not import EBUCore wholesale or impose a track model on film.
- Item and Carrier are first-class alternatives for stream attachment. Archives need not create Carrier records to describe streams. Existing W/V/M/I language descriptions remain; a stream can reference the same LanguageUsage node. No language or characteristic assertions propagate automatically between levels.
- Keep storage media and stored digital objects separate where possible. Storage/content and package-component relationships are distinct from hasStream and remain unresolved with Carrier (§4.8). No new hasContent/isContentOf relation is introduced here.
- Multiple files should have distinct object descriptions when their formats and streams must be associated precisely. Multiple hasFormat values plus unassigned streams on one summary Item do not establish those associations.
- Ordinary film description remains unchanged. A picture-and-sepmag set can link to two carriers with 35mmFilm and 35mmMagneticFilm; no DigitalStream is needed. Summary Items may report component formats, without asserting a single physical roll has both formats.
- Streams are optional. Unknown stream inventory may be omitted; transforms must not invent stream counts or codec/language associations from unrelated summary values. SubtitleStream describes independently encoded embedded subtitles, not burned-in text. Still-image/sequence structure, subtitle codecs, technical measurements, and fixity are not comprehensively modelled here.
- RDFS domains infer types, rather than validate forbidden combinations. No maximum cardinality, disjointness, or SHACL constraints are added in this change.

### Examples

See `example/DigitalStream.ttl` for executable RDF examples of Item-only description, Carrier-level description, shared language-usage nodes, embedded subtitles, and a picture/sepmag film set. The examples do not introduce speculative storage or package relationships.

```turtle
# An archive with no inventory entity below Item.
:file a fiaf:Item ;
    fiaf:hasFormat fiaf:MKV ;
    fiaf:hasStream
        [ a fiaf:VideoStream ; fiaf:hasVideoCodec fiaf:FFV1 ],
        [ a fiaf:AudioStream ; fiaf:hasAudioCodec fiaf:PCM ;
          fiaf:hasSoundCharacteristic [ a fiaf:Sound ;
              fiaf:hasSoundChannelConfiguration fiaf:Stereo ] ] .

# An archive describing individual digital carriers.
:holding a fiaf:Item ; fiaf:hasCarrier :file-carrier .
:file-carrier a fiaf:Carrier ;
    fiaf:hasFormat fiaf:WAV ;
    fiaf:hasStream [ a fiaf:AudioStream ; fiaf:hasAudioCodec fiaf:PCM ] .
```

### Migration

`hasFormat` continues to point directly to format IRIs; it does not change to blank-node descriptions. Codec IRIs are preserved, but codec values previously emitted via hasFormat must move to hasVideoCodec/hasAudioCodec on a stream. Existing format queries will no longer find codecs through the Format hierarchy. A source naming a specific codec can support a minimally described stream; unknown additional streams and characteristics are left unstated. Coarse Manifestation-level codec mappings require review because hasStream deliberately has only Item ∪ Carrier as its domain.
