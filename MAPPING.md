# NB avcatalogue → FIAFcore mapping report

How the National Library of Norway (NB) **avcatalogue** harvest bundles are
mapped to [FIAFcore](https://dev.fiafcore.org) by the transform in
`transform/nb/` (`nb_fiafcore/`). Both the Python transform and the generated
`nln.xsl` XSLT follow these tables.

This document is a snapshot derived from the mapping code
(`nb_fiafcore/tables.py`, `levels.py`, `agents.py`, `iri.py`) and the dataset
scan (`report.md` / `inventory.json`, 14,852 bundles: 14,852 Works, 14,821
Manifestations, 36,163 Items, 124,027 Item_Parts).

Conventions:

- **source field** is the XML tag path inside a `fiafcore-bundle` record.
- **observed n** is the number of records carrying that value in the scanned
  dataset. Counts come from the top-50 histogram per field, so `—` means the
  value is outside the top 50 (or never observed).
- **target** is the FIAFcore local name; `fiaf:` expands to
  `https://dev.fiafcore.org/`.
- A `⚠` after a target means it is not a declared class in
  `nb_fiafcore/ontology_classes.py` (regenerate that file with
  `scripts/refresh_ontology_classes.py`).

## 1. Namespaces

| prefix | IRI |
|---|---|
| `fiaf:` | `https://dev.fiafcore.org/` |
| `rdf:` | `http://www.w3.org/1999/02/22-rdf-syntax-ns#` |
| `rdfs:` | `http://www.w3.org/2000/01/rdf-schema#` |
| `dcterms:` | `http://purl.org/dc/terms/` |
| `nln://extension/` | NLN extension classes with no FIAFcore equivalent |

## 2. Entity model

```
WORK (fiaf:MonographicWork)
  └─ fiaf:hasManifestation → MANIFESTATION (fiaf:Manifestation + subtype)
        └─ fiaf:hasItem → ITEM (fiaf:Item)
              └─ fiaf:hasCarrier → CARRIER (fiaf:Carrier)
```

Record type → level (from the `depth` attribute of each `<record>`):

| `record_type` | depth | entity |
|---|---|---|
| `WORK` | 0 | Work |
| `MANIFESTATION` | 1 | Manifestation |
| `ITEM` | 2 | Item |
| `ITEM_PART`, `ITEM_PART_DUMMY` | 3 | Carrier |

## 3. IRI patterns

Source prefix `nln`; `{priref}` is the avcatalogue record id, `{slug}` an
organisation slug.

| entity | IRI |
|---|---|
| Work | `nln://resource/work/{priref}` |
| Manifestation | `nln://resource/manifestation/{priref}` |
| Item | `nln://resource/item/{priref}` |
| Carrier | `nln://resource/carrier/{priref}` |
| Agent (person/body) | `nln://resource/agent/{priref}` |
| Organisation | `nln://resource/agent/{slug}` |
| Identifier | `nln://identifier/{kind}/{priref}` (alternatives add `/{index}`) |
| Extension class | `nln://extension/iso3166-3/{code}`, `nln://extension/format/{slug}`, `nln://extension/language/{code}` |

`{kind}` is one of `work`, `manifestation`, `item`, `carrier`, `agent`.
Identifier `index` is omitted for the primary identifier and starts at `1` for
kept alternative numbers.

## 4. Field → property mappings

### 4.1 Work (`emit_work`)

| source field | condition | predicate | object | notes |
|---|---|---|---|---|
| `priref` | always | `rdf:type` | `fiaf:MonographicWork` | subject = `nln://resource/work/{priref}` |
| `Title/title` | per `<Title>` group | `fiaf:hasTitle` → `fiaf:hasTitleValue` | blank node + literal | one title node per group |
| `Title/title.type/term` | per title | `rdf:type` (on title node) | `fiaf:[TitleType]` | see §6.12 title.type; default `fiaf:Title` |
| `Title/title.language/term` | present | language tag on `fiaf:hasTitleValue` | BCP-47 literal | `Norsk` → `"…"@no` (§6.23) |
| `Title/title.main = x` | first main (or first title) | `rdfs:label` | literal | preferred title |
| `object_number` | present | `fiaf:hasIdentifier` | `nln://identifier/work/{priref}` | value + authority `nln`; `rdf:type fiaf:Identifier` |
| `Alternative_number/alternative_number` | `alternative_number.type/term` ∈ §6 alt-number keep | `fiaf:hasIdentifier` | `nln://identifier/work/{priref}/{i}` | index `i` starts at 1 |
| `production_country/term` | per value | `fiaf:hasCountry` | `fiaf:[Country]` | §6.1 country; historical → extension |
| `content.genre/term` | kind `form` | `fiaf:hasForm` | `fiaf:[Form]` | §6.6 content.genre |
| `content.genre/term` | kind `genre` | `fiaf:hasGenre` | `fiaf:[Genre]` | §6.6 content.genre |
|  | always | `fiaf:hasEvent` | blank node `rdf:type fiaf:ProductionEvent` | parent event for all credits |
| `Dating/dating.type`, `dating.date.start`, `dating.notes` | type → `ProductionEvent` | `fiaf:hasDate`, `rdfs:comment` (on the ProductionEvent) | literal | same event as credits |
| `Dating/...` | other types | `fiaf:hasEvent` | blank node `fiaf:[Event]` | §6.14 dating.type; date + comment |
| `Credits/credit.name/name`, `credit.name/priref`, `credit.type/term` | `name` present | `fiaf:hasEvent`(prod.) → `fiaf:hasActivity` → `fiaf:hasAgent` | blank node `fiaf:[Activity]` → agent IRI | §6.13 credit.type; default `fiaf:Activity`; agent node emitted once per priref |
| `Credits/credit.notes` | present | `rdfs:comment` (on the activity) | literal | role detail, e.g. "Fokuspuller" |
|  | (agent kind) | `rdf:type` (on the agent) | `fiaf:Person` / `fiaf:Organisation` / `fiaf:Agent` | §6.21 credit.type → agent kind |
| `award`, `award.notes` | per value | `fiaf:hasEvent` | blank node `fiaf:AwardOrNominationEvent` → `fiaf:hasAchievement` literal | free text goes to `hasAchievement` |
| `nomination` | present | `fiaf:hasEvent` | blank node `fiaf:AwardOrNominationEvent` → `fiaf:nominationOnly true` |  |
| `censor_rating/term` | per value | `fiaf:hasEvent` | blank node `fiaf:RatingEvent` → `fiaf:hasVerdict` literal | one event per rating |
| `Language/language/term`, `language.usage/term`, `language.notes` | per `<Language>` group | `fiaf:hasLanguageUsage` | blank node `fiaf:[LanguageUsage]` → `fiaf:hasLanguage` | §6.23 language.usage; `Uten tale` → `fiaf:NoDialogue` usage; `language.notes` → `rdfs:comment` |
| `Description/description`, `description.type/term` | type publishable | `dcterms:description` | literal (language-tagged) | §6.19 description.type; internal types skipped |
| `Related_object/related_object.record_type/value`, `.reference.lref`, `.association/term` | `record_type=WORK`, `lref` ≠ self | `fiaf:hasWork` | `nln://resource/work/{lref}` | typed association |
| `Related_object/...` | association missing/`Mangler type` | `rdfs:seeAlso` | `nln://resource/work/{lref}` | untyped relation |
| child record (depth 1) |  | `fiaf:hasManifestation` | manifestation IRI |  |

### 4.2 Manifestation (`emit_manifestation`)

| source field | condition | predicate | object | notes |
|---|---|---|---|---|
| `priref` | always | `rdf:type` | `fiaf:Manifestation` or subtype | subject = `nln://resource/manifestation/{priref}`; subtype from §6 manifestation_type |
| `Title/*` (via work-label helper) | title present | `rdfs:label` | literal | preferred title |
| `object_number` | present | `fiaf:hasIdentifier` | `nln://identifier/manifestation/{priref}` | authority `nln` |
| `Alternative_number/*` | type kept | `fiaf:hasIdentifier` | `nln://identifier/manifestation/{priref}/{i}` | §6 alt-number keep |
| `colour_type/term` | per value | `fiaf:hasColourCharacteristic` | `fiaf:[Colour]` | §6 colour_type; possibly several |
| `sound/value` | per value | `fiaf:hasSoundCharacteristic` | `fiaf:[Sound]` | §6 sound.value |
| `Runtime_main/runtime.hours` / `runtime.minutes` / `runtime.seconds` | any present | `fiaf:hasExtent` | blank node `fiaf:Minute` → `fiaf:hasExtentValue` | total whole minutes |
| `censor_rating/term` | per value | `fiaf:hasEvent` | blank node `fiaf:RatingEvent` → `fiaf:hasVerdict` literal |  |
| child record (depth 2) |  | `fiaf:hasItem` | item IRI |  |

### 4.3 Item (`emit_item`)

| source field | condition | predicate | object | notes |
|---|---|---|---|---|
| `priref` | always | `rdf:type` | `fiaf:Item` | subject = `nln://resource/item/{priref}` |
| `object_number` | present | `fiaf:hasIdentifier` | `nln://identifier/item/{priref}` | authority `nln` |
| `Alternative_number/*` | type kept | `fiaf:hasIdentifier` | `nln://identifier/item/{priref}/{i}` | §6 alt-number keep |
| `gauge/term` | per value | `fiaf:hasFormat` | `fiaf:[Gauge]` or extension | §6 gauge; `28mm` → `nln://extension/format/28mmFilm` |
| `Carrier_type/carrier_type_specific/term` | kind `element` | `fiaf:isElement` | `fiaf:[Element]` | §6 carrier_type (the "elements") |
| `Carrier_type/carrier_type_specific/term` | kind `format` | `fiaf:hasFormat` | `fiaf:[Format]` | §6 carrier_type |
| `Carrier_type/carrier_type_specific/term` | kind `sound` (`Sepmag`) | `fiaf:hasSoundStandard` (on sound node) | `fiaf:Magnetic` | attached to the sound-characteristic node |
| `Material/material/term` | per value | `fiaf:hasBase` | `fiaf:[Base]` | §6.9 material; possibly several |
| `Stock/stock/term` | per `<Stock>` group | `fiaf:hasStock` | `nln://resource/stock/{priref}/{n}` typed `fiaf:[Stock]` or generic `fiaf:Stock` | §6.22 stock; `rdfs:label` = manufacturer |
| `Stock/stock_formulation/term`, `stock_batch_no` | present | `fiaf:hasStockCode` (on the stock node) | literal | one code per value |
| `colour_type/term` | per value | `fiaf:hasColourCharacteristic` | `fiaf:[Colour]` | §6 colour_type |
| `sound_type/term` | first mapped value | `fiaf:hasSoundCharacteristic` | blank node `fiaf:Sound` / `fiaf:Silent` / `fiaf:Mute` | §6 sound_type |
| `sound_system/term` | per value | `fiaf:hasSoundStandard` / `fiaf:hasNoiseReduction` / `fiaf:hasSoundChannelConfiguration` (on sound node) | `fiaf:[Standard]` | §6 sound_system; creates a `fiaf:Sound` node if needed; one node per soundtrack |
| `broadcast_standard/value` | per value | `fiaf:hasBroadcastStandard` | `fiaf:[Standard]` | §6 broadcast_standard |
| `Dimension/dimension.unit/term`, `dimension.value` | both present | `fiaf:hasExtent` | blank node `fiaf:[Unit]` → `fiaf:hasExtentValue` | §6 dimension.unit |
| `Language/language/term`, `language.usage/term`, `language.notes` | per `<Language>` group | `fiaf:hasLanguageUsage` | blank node `fiaf:[LanguageUsage]` → `fiaf:hasLanguage` `fiaf:[Language]` | §6.23 language.usage; `Uten tale` → `fiaf:NoDialogue` usage; some → extension; `language.notes` → `rdfs:comment` |
| `item_status/term` | per value | `fiaf:hasStatus` | `fiaf:Access` / `fiaf:Preservation` | §6.17 item_status; `None` values skipped |
|  | always | `fiaf:hasHoldingInstitution` | `nln://resource/agent/nln` | The National Library of Norway |
| child record (depth 3) |  | `fiaf:hasCarrier` | carrier IRI |  |

### 4.4 Carrier (`emit_carrier`)

| source field | condition | predicate | object | notes |
|---|---|---|---|---|
| `priref` | always | `rdf:type` | `fiaf:Carrier` | subject = `nln://resource/carrier/{priref}` |
| `object_number` | present | `fiaf:hasIdentifier` | `nln://identifier/carrier/{priref}` | authority `nln` |
| `Alternative_number/*` | type kept | `fiaf:hasIdentifier` | `nln://identifier/carrier/{priref}/{i}` | §6 alt-number keep |
| `Label/label.note` | first non-empty | `rdfs:label` | literal | carrier note |

## 5. Shared node builders

| builder | subject | triples |
|---|---|---|
| `emit_agent` | `nln://resource/agent/{priref}` | `rdf:type fiaf:Person` / `fiaf:Organisation` / `fiaf:Agent` (kind); `rdfs:label "{name}"`; `fiaf:hasIdentifier` → `nln://identifier/agent/{priref}` (authority `nln`) |
| `emit_org` | `nln://resource/agent/{slug}` | `rdf:type fiaf:Organisation`; `rdfs:label` from §6 orgs |
| `emit_identifier` | `nln://identifier/{kind}/{priref}[/{i}]` | `rdf:type fiaf:Identifier`; `fiaf:hasIdentifierValue` literal; `fiaf:hasIdentifierAuthority` org (when given) |
| `emit_title` | blank node | `rdf:type fiaf:[TitleType]`; `fiaf:hasTitleValue` literal (BCP-47 tagged when `title.language` present) |
| `emit_event` | blank node | `rdf:type fiaf:[Event]`; `fiaf:hasDate` literal (optional); `rdfs:comment` literal (optional) |
| `emit_award_event` | blank node | `rdf:type fiaf:AwardOrNominationEvent`; `fiaf:hasAchievement` literal (optional); `fiaf:nominationOnly true` (optional) |
| `emit_activity` | blank node | `rdf:type fiaf:[Activity]`; `fiaf:hasAgent` agent (optional); `rdfs:comment` (optional) |
| `emit_country_extension` | `nln://extension/iso3166-3/{code}` | `rdf:type owl:Class`; `rdfs:subClassOf fiaf:Country`; `rdfs:label` (en/nb) |
| `emit_format_extension` | `nln://extension/format/{slug}` | `rdf:type owl:Class`; `rdfs:subClassOf fiaf:[parent]`; `rdfs:label` |
| `emit_language_extension` | `nln://extension/language/{code}` | `rdf:type owl:Class`; `rdfs:subClassOf fiaf:Language`; `rdfs:label` (en/nb) |

## 6. Controlled-vocabulary tables

Each row is one source value. **disposition**: *mapped* emits the target;
*dropped* is a recognised value with no FIAFcore target (the transform does
**not** count it as a coverage miss); *extension* emits an `nln://extension/`
subclass. Values absent from a table are reported as coverage misses
(§9).

### 6.1 `production_country/term` → `fiaf:hasCountry` (COUNTRY)

| source value | observed n | target | disposition |
|---|---|---|---|
| Norge | 4793 | `fiaf:Norway` | mapped |
| Sverige | 809 | `fiaf:Sweden` | mapped |
| Danmark | 555 | `fiaf:Denmark` | mapped |
| Finland | 136 | `fiaf:Finland` | mapped |
| Island | 56 | `fiaf:Iceland` | mapped |
| Tyskland | — | `fiaf:Germany` | mapped |
| Vest-Tyskland | — | `fiaf:Germany` | mapped |
| Øst-Tyskland | — | `fiaf:Germany` | mapped |
| Tyskland (inkluderer Vest-Tyskland 1949-1990) | 602 | `fiaf:Germany` | mapped |
| Øst-Tyskland (1949-1990) | — | `fiaf:Germany` | mapped |
| Frankrike | 763 | `fiaf:France` | mapped |
| Storbritannia | 662 | `fiaf:UnitedKingdomOfGreatBritainAndNorthernIreland` | mapped |
| England | — | `fiaf:UnitedKingdomOfGreatBritainAndNorthernIreland` | mapped |
| Skottland | — | `fiaf:UnitedKingdomOfGreatBritainAndNorthernIreland` | mapped |
| Wales | — | `fiaf:UnitedKingdomOfGreatBritainAndNorthernIreland` | mapped |
| USA | 19 | `fiaf:UnitedStatesOfAmerica` | mapped |
| Sambandsstatene | — | `fiaf:UnitedStatesOfAmerica` | mapped |
| Forente stater | 2600 | `fiaf:UnitedStatesOfAmerica` | mapped |
| Canada | 137 | `fiaf:Canada` | mapped |
| Italia | 269 | `fiaf:Italy` | mapped |
| Spania | 91 | `fiaf:Spain` | mapped |
| Nederland | 65 | `fiaf:NetherlandsKingdomOfThe` | mapped |
| Belgia | 84 | `fiaf:Belgium` | mapped |
| Sveits | 31 | `fiaf:Switzerland` | mapped |
| Østerrike | 51 | `fiaf:Austria` | mapped |
| Polen | 44 | `fiaf:Poland` | mapped |
| Tsjekkia | 37 | `fiaf:Czechia` | mapped |
| Tsjekkoslovakia | 8 | `fiaf:Czechia` | mapped |
| Slovakia | — | `fiaf:Slovakia` | mapped |
| Ungarn | 23 | `fiaf:Hungary` | mapped |
| Romania | 13 | `fiaf:Romania` | mapped |
| Bulgaria | — | `fiaf:Bulgaria` | mapped |
| Russland | 38 | `fiaf:RussianFederation` | mapped |
| Japan | 85 | `fiaf:Japan` | mapped |
| Kina | 48 | `fiaf:China` | mapped |
| India | 14 | `fiaf:India` | mapped |
| Australia | 76 | `fiaf:Australia` | mapped |
| New Zealand | 15 | `fiaf:NewZealand` | mapped |
| Brasil | 13 | `fiaf:Brazil` | mapped |
| Argentina | 31 | `fiaf:Argentina` | mapped |
| Mexico | 47 | `fiaf:Mexico` | mapped |
| Sør-Afrika | 13 | `fiaf:SouthAfrica` | mapped |
| Israel | 15 | `fiaf:Israel` | mapped |
| Tyrkia | 21 | `fiaf:Turkiye` | mapped |
| Portugal | 9 | `fiaf:Portugal` | mapped |
| Hellas | 19 | `fiaf:Greece` | mapped |
| Irland | 52 | `fiaf:Ireland` | mapped |
| Ireland | — | `fiaf:Ireland` | mapped |
| Luxembourg | — | `fiaf:Luxembourg` | mapped |
| Luxemburg | 13 | `fiaf:Luxembourg` | mapped |
| Estland | — | `fiaf:Estonia` | mapped |
| Latvia | — | `fiaf:Latvia` | mapped |
| Litauen | — | `fiaf:Lithuania` | mapped |
| Kroatia | 9 | `fiaf:Croatia` | mapped |
| Serbia | — | `fiaf:Serbia` | mapped |
| Slovenia | — | `fiaf:Slovenia` | mapped |
| Bosnia-Hercegovina | — | `fiaf:BosniaAndHerzegovina` | mapped |
| Egypt | — | `fiaf:Egypt` | mapped |
| Marokko | — | `fiaf:Morocco` | mapped |
| Tunisia | 14 | `fiaf:Tunisia` | mapped |
| Algerie | — | `fiaf:Algeria` | mapped |
| Kenya | — | `fiaf:Kenya` | mapped |
| Nigeria | — | `fiaf:Nigeria` | mapped |
| Sør-Korea | 65 | `fiaf:KoreaRepublicOf` | mapped |
| Filippinene | — | `fiaf:Philippines` | mapped |
| Thailand | — | `fiaf:Thailand` | mapped |
| Vietnam | — | `fiaf:VietNam` | mapped |
| Indonesia | — | `fiaf:Indonesia` | mapped |
| Pakistan | — | `fiaf:Pakistan` | mapped |
| Iran | 25 | `fiaf:IranIslamicRepublicOf` | mapped |
| Irak | — | `fiaf:Iraq` | mapped |
| Syria | — | `fiaf:SyrianArabRepublic` | mapped |
| Libanon | 10 | `fiaf:Lebanon` | mapped |
| Jordan | — | `fiaf:Jordan` | mapped |
| Saudi-Arabia | — | `fiaf:SaudiArabia` | mapped |
| De forente arabiske emirater | — | `fiaf:UnitedArabEmirates` | mapped |
| Cuba | — | `fiaf:Cuba` | mapped |
| Chile | — | `fiaf:Chile` | mapped |
| Peru | — | `fiaf:Peru` | mapped |
| Colombia | 12 | `fiaf:Colombia` | mapped |
| Venezuela | — | `fiaf:VenezuelaBolivarianRepublicOf` | mapped |
| Uruguay | 9 | `fiaf:Uruguay` | mapped |
| Bolivia | — | `fiaf:BoliviaPlurinationalStateOf` | mapped |
| Paraguay | — | `fiaf:Paraguay` | mapped |
| Ecuador | — | `fiaf:Ecuador` | mapped |
| Puerto Rico | — | `fiaf:PuertoRico` | mapped |
| Ghana | — | `fiaf:Ghana` | mapped |
| Senegal | — | `fiaf:Senegal` | mapped |
| Kamerun | — | `fiaf:Cameroon` | mapped |
| Burkina Faso | — | `fiaf:BurkinaFaso` | mapped |
| Etiopia | — | `fiaf:Ethiopia` | mapped |
| Mongolia | — | `fiaf:Mongolia` | mapped |
| Kasakhstan | — | `fiaf:Kazakhstan` | mapped |
| Georgia | — | `fiaf:Georgia` | mapped |
| Armenia | — | `fiaf:Armenia` | mapped |
| Usbekistan | — | `fiaf:Uzbekistan` | mapped |
| Hviterussland | — | `fiaf:Belarus` | mapped |
| Ukraina | — | `fiaf:Ukraine` | mapped |
| Moldova | — | `fiaf:MoldovaRepublicOf` | mapped |
| Palestina | — | `fiaf:PalestineStateOf` | mapped |
| Nord-Makedonia | — | `fiaf:NorthMacedonia` | mapped |
| Montenegro | — | `fiaf:Montenegro` | mapped |
| Malta | — | `fiaf:Malta` | mapped |
| Kypros | — | `fiaf:Cyprus` | mapped |
| Liechtenstein | — | `fiaf:Liechtenstein` | mapped |
| Monaco | — | `fiaf:Monaco` | mapped |
| Singapore | — | `fiaf:Singapore` | mapped |
| Hongkong | 48 | `fiaf:HongKong` | mapped |
| Taiwan | 13 | `fiaf:TaiwanProvinceOfChina` | mapped |
| Sri Lanka | — | `fiaf:SriLanka` | mapped |
| SRI LANKA | — | `fiaf:SriLanka` | mapped |
| Bangladesh | — | `fiaf:Bangladesh` | mapped |
| Nepal | — | `fiaf:Nepal` | mapped |
| Myanmar | — | `fiaf:Myanmar` | mapped |
| Zimbabwe | — | `fiaf:Zimbabwe` | mapped |
| Zambia | — | `fiaf:Zambia` | mapped |
| Namibia | — | `fiaf:Namibia` | mapped |
| Mosambik | — | `fiaf:Mozambique` | mapped |
| Angola | — | `fiaf:Angola` | mapped |
| Madagaskar | — | `fiaf:Madagascar` | mapped |
| Trinidad og Tobago | — | `fiaf:TrinidadAndTobago` | mapped |
| Jamaica | — | `fiaf:Jamaica` | mapped |
| Bahamas | — | `fiaf:Bahamas` | mapped |
| Bermuda | — | `fiaf:Bermuda` | mapped |
| Man | — | `fiaf:IsleOfMan` | mapped |
| Martinique | — | `fiaf:Martinique` | mapped |
| Kapp Verde | — | `fiaf:CaboVerde` | mapped |
| Guinea-Bissau | — | `fiaf:GuineaBissau` | mapped |
| Guinea | — | `fiaf:Guinea` | mapped |
| Niger | — | `fiaf:Niger` | mapped |
| Tsjad | — | `fiaf:Chad` | mapped |
| Costa Rica | — | `fiaf:CostaRica` | mapped |
| Den dominikanske republikk | — | `fiaf:DominicanRepublic` | mapped |
| Nicaragua | — | `fiaf:Nicaragua` | mapped |
| Panama | — | `fiaf:Panama` | mapped |
| Qatar | 18 | `fiaf:Qatar` | mapped |
| Kuwait | — | `fiaf:Kuwait` | mapped |
| Bhutan | — | `fiaf:Bhutan` | mapped |
| Grønland | — | `fiaf:Greenland` | mapped |
| Færøyene | — | `fiaf:FaroeIslands` | mapped |
| Malaysia | — | `fiaf:Malaysia` | mapped |
| Afghanistan | — | `fiaf:Afghanistan` | mapped |
| Elfenbeinskysten | — | `fiaf:CoteDivoire` | mapped |
| Albania | — | `fiaf:Albania` | mapped |
| Guatemala | — | `fiaf:Guatemala` | mapped |
| Somalia | — | `fiaf:Somalia` | mapped |
| Sudan | — | `fiaf:Sudan` | mapped |
| Tanzania | — | `fiaf:TanzaniaUnitedRepublicOf` | mapped |

**Extensions** (historical countries, `rdfs:subClassOf fiaf:Country`):

| source value | observed n | target | disposition |
|---|---|---|---|
| Sovjetunionen | 69 | `nln://extension/iso3166-3/SU` (Soviet Union / Sovjetunionen) | extension |
| Jugoslavia | 23 | `nln://extension/iso3166-3/YU` (Yugoslavia / Jugoslavia) | extension |

Values observed in the dataset but in neither table are coverage misses. In
the scanned dataset all observed countries were covered.

### 6.2 `manifestation_type/term` → `rdf:type` on Manifestation (MANIFESTATION_TYPE)

| source value | observed n | target | disposition |
|---|---|---|---|
| Ukjent | 14812 | `fiaf:Manifestation` | mapped (base class) |
| Kino | — | `fiaf:TheatricalManifestation` | mapped |
| Kinofilm | — | `fiaf:TheatricalManifestation` | mapped |
| Theatrical | — | `fiaf:TheatricalManifestation` | mapped |
| Fjernsyn | — | `fiaf:BroadcastManifestation` | mapped |
| TV | — | `fiaf:BroadcastManifestation` | mapped |
| TV-visning | — | `fiaf:BroadcastManifestation` | mapped |
| Video | — | `fiaf:HomeViewingManifestation` | mapped |
| Hjemmevideo | — | `fiaf:HomeViewingManifestation` | mapped |
| Internett | — | `fiaf:InternetManifestation` | mapped |
| Nett | — | `fiaf:InternetManifestation` | mapped |
| Restaurering | — | `fiaf:RestorationManifestation` | mapped |
| Bevaring | — | `fiaf:PreservationManifestation` | mapped |
| Forhåndsvisning | — | `fiaf:PreReleaseManifestation` | mapped |
| LB: Visningselementer | 4 | `fiaf:Manifestation` | mapped (base class) |
| LB: Produksjonselementer | 1 | `fiaf:Manifestation` | mapped (base class) |
| LB: Videoverføring | 1 | `fiaf:Manifestation` | mapped (base class) |
| LB: Bevaring digital | 1 | `fiaf:Manifestation` | mapped (base class) |
| LB: Digitisering | 1 | `fiaf:Manifestation` | mapped (base class) |

### 6.3 `colour_type/term` → `fiaf:hasColourCharacteristic` (COLOUR_TYPE)

| source value | observed n | target | disposition |
|---|---|---|---|
| Farger | 78046 | `fiaf:Colour` | mapped |
| Farge | — | `fiaf:Colour` | mapped |
| Svart/hvitt | 24780 | `fiaf:BlackAndWhite` | mapped |
| Svart-hvitt | — | `fiaf:BlackAndWhite` | mapped |
| Sort-hvitt | — | `fiaf:BlackAndWhite` | mapped |
| Sorthvitt | — | `fiaf:BlackAndWhite` | mapped |
| Sv/hv | 3431 | `fiaf:BlackAndWhite` | mapped |
| Svart/hvitt og farger | 983 | `fiaf:BlackAndWhite`, `fiaf:Colour` | mapped (multiple) |
| Farger & sv/hv | 188 | `fiaf:Colour`, `fiaf:BlackAndWhite` | mapped (multiple) |
| Tintet | 484 | `fiaf:Tinted` | mapped |
| Tintet og/eller tonet | 736 | `fiaf:Tinted`, `fiaf:Toned` | mapped (multiple) |
| Både tintet & tonet | 33 | `fiaf:Tinted`, `fiaf:Toned` | mapped (multiple) |
| Tintet & Tonet | 2 | `fiaf:Tinted`, `fiaf:Toned` | mapped (multiple) |
| Tonet | 14 | `fiaf:Toned` | mapped |
| Stensilkolorert | 1 | `fiaf:Colour` | mapped |
| Ingen | 868 | — | dropped (recognised, no target) |
| Annet, se merknad | 36 | — | dropped (recognised, no target) |

### 6.4 `sound/value` → `fiaf:hasSoundCharacteristic` (SOUND_VALUE)

| source value | observed n | target | disposition |
|---|---|---|---|
| LYD | 20711 | `fiaf:Sound` | mapped |
| STUM | 5 | `fiaf:Silent` | mapped |
| MUTE | — | `fiaf:Mute` | mapped |

### 6.5 `sound_type/term` → `fiaf:hasSoundCharacteristic` (SOUND_TYPE)

| source value | observed n | target | disposition |
|---|---|---|---|
| Lyd | 8262 | `fiaf:Sound` | mapped |
| Stum | 1952 | `fiaf:Silent` | mapped |
| Stille | — | `fiaf:Silent` | mapped |
| Uten lyd | 10714 | `fiaf:Mute` | mapped |

### 6.6 `content.genre/term` → `fiaf:hasForm` / `fiaf:hasGenre` (CONTENT_GENRE)

| source value | observed n | predicate | target | disposition |
|---|---|---|---|---|
| Spillefilm | 14852 | `fiaf:hasForm` | `fiaf:FeatureFilm` | mapped (form) |
| Kortfilm (fiksjon, novellefilm o.l.) | 11 | `fiaf:hasForm` | `fiaf:ShortFilm` | mapped (form) |
| Kortfilm | — | `fiaf:hasForm` | `fiaf:ShortFilm` | mapped (form) |
| Trailer | 8 | `fiaf:hasForm` | `fiaf:Trailer` | mapped (form) |
| Amatørfilm | — | `fiaf:hasForm` | `fiaf:AmateurFilm` | mapped (form) |
| Amatør | — | `fiaf:hasForm` | `fiaf:AmateurFilm` | mapped (form) |
| Hjemmefilm | — | `fiaf:hasForm` | `fiaf:HomeMovie` | mapped (form) |
| For barn/unge | 291 | `fiaf:hasGenre` | `fiaf:ChildrensFilm` | mapped (genre) |
| Animasjonsfilm | 107 | `fiaf:hasGenre` | `fiaf:AnimationFilm` | mapped (genre) |
| Animasjon, tegnefilm | 69 | `fiaf:hasGenre` | `fiaf:AnimationFilm` | mapped (genre) |
| Animasjonsinnslag | 10 | `fiaf:hasGenre` | `fiaf:AnimationFilm` | mapped (genre) |
| Komedie | 83 | `fiaf:hasGenre` | `fiaf:ComedyFilm` | mapped (genre) |
| Drama | 50 | `fiaf:hasGenre` | `fiaf:DramaFilm` | mapped (genre) |
| Musikkfilm/-video | 5 | `fiaf:hasGenre` | `fiaf:MusicFilm` | mapped (genre) |
| Undervisning | 2 | `fiaf:hasGenre` | `fiaf:EducationalFilm` | mapped (genre) |
| Fjernsynsfilm | 66 | — | — | dropped (recognised, no target) |
| Dokumentarfilm | 6 | — | — | dropped (recognised, no target) |
| Underholdning | 5 | — | — | dropped (recognised, no target) |
| Reklame | 4 | — | — | dropped (recognised, no target) |
| W - Pop og rock | 1 | — | — | dropped (recognised, no target) |

### 6.7 `gauge/term` → `fiaf:hasFormat` (GAUGE)

| source value | observed n | target | disposition |
|---|---|---|---|
| 35mm | 108418 | `fiaf:35mmFilm` | mapped |
| 16mm | 3192 | `fiaf:16mmFilm` | mapped |
| 17.5mm | 971 | `fiaf:17.5mmFilm` | mapped |
| 17,5mm | — | `fiaf:17.5mmFilm` | mapped |
| 9.5mm | — | `fiaf:9.5mmFilm` | mapped |
| 9,5mm | — | `fiaf:9.5mmFilm` | mapped |
| 8mm | — | `fiaf:8mmFilm` | mapped |
| 70mm | 6 | `fiaf:70mmFilm` | mapped |
| Super 8 | — | `fiaf:Super8mmFilm` | mapped |
| Super 16 | — | `fiaf:Super16mmFilm` | mapped |
| Super8 | — | `fiaf:Super8mmFilm` | mapped |
| Super16 | — | `fiaf:Super16mmFilm` | mapped |
| 1/2" | 949 | `fiaf:VideoFormat` | mapped |
| 3/4" | 776 | `fiaf:VideoFormat` | mapped |
| 1" | 381 | `fiaf:OneInchVideotape` | mapped |
| 2" | 2 | `fiaf:TwoInchVideotape` | mapped |
| 1/4" Audio Tape | 38 | `fiaf:QuerterInchAudiotape` | mapped |
| Annet, se merknad | 18 | — | dropped (recognised, no target) |

**Extensions:**

| source value | observed n | target | disposition |
|---|---|---|---|
| 28mm | 11 | `nln://extension/format/28mmFilm` (`rdfs:subClassOf fiaf:FilmFormat`) | extension |

### 6.8 `Carrier_type/carrier_type_specific/term` (CARRIER_TYPE_SPECIFIC)

`kind=element` → `fiaf:isElement`; `kind=format` → `fiaf:hasFormat`;
`kind=sound` → `fiaf:hasSoundStandard`; `ignore` → no target.

| source value | observed n | predicate | target | disposition |
|---|---|---|---|---|
| Bildenegativ | 5255 | `fiaf:isElement` | `fiaf:OriginalNegative` | mapped (element) |
| Kameranegativ | 2093 | `fiaf:isElement` | `fiaf:OriginalNegative` | mapped (element) |
| Negativ | 58 | `fiaf:isElement` | `fiaf:OriginalNegative` | mapped (element) |
| A-/B-rull negativ | 408 | `fiaf:isElement` | `fiaf:OriginalNegative` | mapped (element) |
| Duplikat negativ | 2274 | `fiaf:isElement` | `fiaf:DuplicateNegative` | mapped (element) |
| Cri-negativ | 51 | `fiaf:isElement` | `fiaf:DuplicateNegative` | mapped (element) |
| Duplikat positiv | 4846 | `fiaf:isElement` | `fiaf:DuplicatePositive` | mapped (element) |
| Lydnegativ | 6762 | `fiaf:isElement` | `fiaf:SoundNegative` | mapped (element) |
| Lydpositiv | 260 | `fiaf:isElement` | `fiaf:SoundPositive` | mapped (element) |
| Visningskopi | 92861 | `fiaf:isElement` | `fiaf:ReleasePrint` | mapped (element) |
| VHS video | 4585 | `fiaf:hasFormat` | `fiaf:VideoFormat` | mapped (format) |
| Super VHS | — | `fiaf:hasFormat` | `fiaf:VideoFormat` | mapped (format) |
| Betamax | 120 | `fiaf:hasFormat` | `fiaf:VideoFormat` | mapped (format) |
| Video8 | — | `fiaf:hasFormat` | `fiaf:VideoFormat` | mapped (format) |
| Hi8 | — | `fiaf:hasFormat` | `fiaf:VideoFormat` | mapped (format) |
| HI-8 | — | `fiaf:hasFormat` | `fiaf:VideoFormat` | mapped (format) |
| VCR | — | `fiaf:hasFormat` | `fiaf:VideoFormat` | mapped (format) |
| Video 2000 | 22 | `fiaf:hasFormat` | `fiaf:VideoFormat` | mapped (format) |
| U-matic High Band | 190 | `fiaf:hasFormat` | `fiaf:VideoFormat` | mapped (format) |
| U-matic SP | 69 | `fiaf:hasFormat` | `fiaf:VideoFormat` | mapped (format) |
| U-matic Low Band | — | `fiaf:hasFormat` | `fiaf:VideoFormat` | mapped (format) |
| DVCAM | 457 | `fiaf:hasFormat` | `fiaf:VideoFormat` | mapped (format) |
| DVC PRO | — | `fiaf:hasFormat` | `fiaf:DVCPROHD` | mapped (format) |
| D-3 | — | `fiaf:hasFormat` | `fiaf:VideoFormat` | mapped (format) |
| D-1 Digital | — | `fiaf:hasFormat` | `fiaf:D1` | mapped (format) |
| Digital Betacam | 1244 | `fiaf:hasFormat` | `fiaf:DigitalBetacam` | mapped (format) |
| Betacam SP | 750 | `fiaf:hasFormat` | `fiaf:BetacamSP` | mapped (format) |
| Betacam Standard | — | `fiaf:hasFormat` | `fiaf:BetacamSP` | mapped (format) |
| HDCam SR | 472 | `fiaf:hasFormat` | `fiaf:HDCAMSR` | mapped (format) |
| HDCAM | 97 | `fiaf:hasFormat` | `fiaf:HDCAMSR` | mapped (format) |
| DVD-video | 3493 | `fiaf:hasFormat` | `fiaf:DVD` | mapped (format) |
| DVD-R | 570 | `fiaf:hasFormat` | `fiaf:DVD` | mapped (format) |
| DVD-audio | — | `fiaf:hasFormat` | `fiaf:DVD` | mapped (format) |
| Blu-ray | 1098 | `fiaf:hasFormat` | `fiaf:BluRay` | mapped (format) |
| Ultra HD Blu-ray | 52 | `fiaf:hasFormat` | `fiaf:BluRay` | mapped (format) |
| Laserdisk | — | `fiaf:hasFormat` | `fiaf:LaserDisc` | mapped (format) |
| CD ISO 9660 (CD-ROM) | — | `fiaf:hasFormat` | `fiaf:CD` | mapped (format) |
| CD-R Blå | — | `fiaf:hasFormat` | `fiaf:CD` | mapped (format) |
| 1" C Videoband | 840 | `fiaf:hasFormat` | `fiaf:OneInchVideotape` | mapped (format) |
| 1" B Videoband | — | `fiaf:hasFormat` | `fiaf:OneInchVideotape` | mapped (format) |
| 1" Digitalbånd | — | `fiaf:hasFormat` | `fiaf:OneInchVideotape` | mapped (format) |
| 2" Analogbånd | — | `fiaf:hasFormat` | `fiaf:TwoInchVideotape` | mapped (format) |
| 1/4" Analogbånd | 111 | `fiaf:hasFormat` | `fiaf:QuerterInchAudiotape` | mapped (format) |
| 1" Analogbånd | — | `fiaf:hasFormat` | `fiaf:OneInchAudiotape` | mapped (format) |
| 1/2" Digitalbånd | — | `fiaf:hasFormat` | `fiaf:DigitalFormat` | mapped (format) |
| Harddisk | 845 | `fiaf:hasFormat` | `fiaf:DigitalFormat` | mapped (format) |
| MO-disk | 194 | `fiaf:hasFormat` | `fiaf:DigitalFormat` | mapped (format) |
| Minnebrikke/-penn | — | `fiaf:hasFormat` | `fiaf:DigitalFormat` | mapped (format) |
| LTO-3 | 17 | `fiaf:hasFormat` | `fiaf:DigitalFormat` | mapped (format) |
| LTO-4 | 44 | `fiaf:hasFormat` | `fiaf:DigitalFormat` | mapped (format) |
| LTO-5 | — | `fiaf:hasFormat` | `fiaf:DigitalFormat` | mapped (format) |
| LTO-6 | 17 | `fiaf:hasFormat` | `fiaf:DigitalFormat` | mapped (format) |
| AIT-3 | — | `fiaf:hasFormat` | `fiaf:DigitalFormat` | mapped (format) |
| DAT/DDS | 139 | `fiaf:hasFormat` | `fiaf:DigitalFormat` | mapped (format) |
| R-DAT | 34 | `fiaf:hasFormat` | `fiaf:DigitalFormat` | mapped (format) |
| Digital audio 8/DTRS-tape | 126 | `fiaf:hasFormat` | `fiaf:DigitalFormat` | mapped (format) |
| Digital Video Cassette | 36 | `fiaf:hasFormat` | `fiaf:DigitalFormat` | mapped (format) |
| Mini-DV (Digital Video Cassette mini) | — | `fiaf:hasFormat` | `fiaf:DigitalFormat` | mapped (format) |
| D6: HD600T | 23 | `fiaf:hasFormat` | `fiaf:DigitalFormat` | mapped (format) |
| Digitial Tape Format | 19 | `fiaf:hasFormat` | `fiaf:DigitalFormat` | mapped (format) |
| Data 8 | — | `fiaf:hasFormat` | `fiaf:DigitalFormat` | mapped (format) |
| DCP 2K | — | `fiaf:hasFormat` | `fiaf:DigitalFormat` | mapped (format) |
| DCP 4K | — | `fiaf:hasFormat` | `fiaf:DigitalFormat` | mapped (format) |
| HDV | — | `fiaf:hasFormat` | `fiaf:DigitalFormat` | mapped (format) |
| Digitalt negativ (fra filmrecorder) | 33 | `fiaf:isElement` | `fiaf:OriginalNegative` | mapped (element) |
| Sepmag | 2299 | `fiaf:hasSoundStandard` | `fiaf:Magnetic` | mapped (sound) |
| Ark (løse) | 3638 | — | — | dropped (recognised, no target) |
| Fotografisk papir | 2424 | — | — | dropped (recognised, no target) |
| Heftet | 626 | — | — | dropped (recognised, no target) |
| Mappe | 586 | — | — | dropped (recognised, no target) |
| Innbundet | 212 | — | — | dropped (recognised, no target) |
| Blad | — | — | — | dropped (recognised, no target) |
| Kartong, brettet | — | — | — | dropped (recognised, no target) |
| Diapositiv | 424 | — | — | dropped (recognised, no target) |
| Produksjonsmateriale | 1448 | — | — | dropped (recognised, no target) |
| Arbeidskopi | 231 | — | — | dropped (recognised, no target) |
| Annet | 202 | — | — | dropped (recognised, no target) |
| Ukjent | — | — | — | dropped (recognised, no target) |
| Blandet | 52 | — | — | dropped (recognised, no target) |
| Omvender | — | — | — | dropped (recognised, no target) |
| Tekster | 81 | — | — | dropped (recognised, no target) |
| MC-kassetter | — | — | — | dropped (recognised, no target) |
| DTS (digital theatrical system) | — | — | — | dropped (recognised, no target) |

### 6.9 `Material/material/term` → `fiaf:hasBase` (MATERIAL)

| source value | observed n | target | disposition |
|---|---|---|---|
| Acetat | 24231 | `fiaf:AcetateBase` | mapped |
| Acetate | — | `fiaf:AcetateBase` | mapped |
| Nitrat | 2803 | `fiaf:NitrateBase` | mapped |
| Polyester | 15458 | `fiaf:PolyesterBase` | mapped |
| Polyethylene-terephthalate (Myler, Melinex) | 2 | `fiaf:PolyesterBase` | mapped |
| Nitrat & safety blandet | 45 | `fiaf:NitrateBase`, `fiaf:AcetateBase` | mapped (multiple) |
| Papir | 3290 | — | dropped (recognised, no target) |
| Annet | 299 | — | dropped (recognised, no target) |
| Ukjent | 128 | — | dropped (recognised, no target) |
| Plast | 20 | — | dropped (recognised, no target) |
| Glass | 10 | — | dropped (recognised, no target) |

### 6.10 `broadcast_standard/value` → `fiaf:hasBroadcastStandard` (BROADCAST_STANDARD)

| source value | observed n | target | disposition |
|---|---|---|---|
| PA | 6734 | `fiaf:PAL` | mapped |
| PAL | — | `fiaf:PAL` | mapped |
| PAL0 | 6 | `fiaf:PAL` | mapped |
| PAL2 | 799 | `fiaf:PAL` | mapped |
| NTSC | 39 | `fiaf:NTSC` | mapped |
| NTSC0 | 8 | `fiaf:NTSC` | mapped |
| NTSC1 | 12 | `fiaf:NTSC` | mapped |
| SECAM | — | `fiaf:SECAM` | mapped |
| HD | 537 | — | dropped (recognised, no target) |
| REGB | 278 | — | dropped (recognised, no target) |

### 6.11 `sound_system/term` → `fiaf:hasSoundStandard` / `fiaf:hasNoiseReduction` / `fiaf:hasSoundChannelConfiguration` (SOUND_SYSTEM)

Values that combine a digital system with an analogue variable-area backup describe **two soundtracks** on the same print and therefore emit two `fiaf:SoundCharacteristic` nodes.

| source value | observed n | target | disposition |
|---|---|---|---|
| Mono | 14110 | `fiaf:hasSoundChannelConfiguration fiaf:Mono` | mapped (channel) |
| Dolby SRD, Variable area | 6503 | `fiaf:DolbyDigital` (digital node) + `fiaf:OpticalVariableArea` (analogue backup node) | mapped (multiple nodes) |
| Variable Area | 4610 | `fiaf:OpticalVariableArea` | mapped |
| Variable Density | 272 | `fiaf:OpticalVariableDensity` | mapped |
| Dolby stereo | 195 | `fiaf:DolbyStereo` | mapped |
| Dolby A | 1879 | `fiaf:hasNoiseReduction fiaf:DolbyA` | mapped (noise reduction) |
| Dolby SR | 1698 | `fiaf:hasNoiseReduction fiaf:DolbySR` | mapped (noise reduction) |
| Dolby u/surround | 131 | `fiaf:DolbyStereo` + `fiaf:hasSoundChannelConfiguration fiaf:Surround` | mapped |
| Dolby Mono | 53 | `fiaf:hasSoundChannelConfiguration fiaf:Mono` + `fiaf:hasNoiseReduction fiaf:Dolby` | mapped |
| Annet, se merknad | 78 | — | dropped (recognised, no target) |
| DTS, Variable area | 39 | `fiaf:DTS` (digital node) + `fiaf:OpticalVariableArea` (analogue backup node) | mapped (multiple nodes) |
| Dolby DS EX, Variable area | 30 | `fiaf:DolbyDigitalSurroundEX` (digital node) + `fiaf:OpticalVariableArea` (analogue backup node) | mapped (multiple nodes) |
| Magnetisk lyd | 298 | `fiaf:Magnetic` | mapped |
| 4-kanals mag.lyd | 28 | `fiaf:FourTrackMagnetic` | mapped |
| Dolby 6-kanals mag.lyd | 18 | `fiaf:SixTrackMagnetic` + `fiaf:hasNoiseReduction fiaf:Dolby` | mapped |
| Dolby A 4-kanals mag.lyd | 18 | `fiaf:FourTrackMagnetic` + `fiaf:hasNoiseReduction fiaf:DolbyA` | mapped |

### 6.12 `Title/title.type/term` → title node `rdf:type` (TITLE_TYPE)

| source value | observed n | target | disposition |
|---|---|---|---|
| Originaltittel | 166900 | `fiaf:TitleProper` | mapped |
| Norsk tittel | 64448 | `fiaf:TitleProper` | mapped |
| Publisert tittel | 1089 | `fiaf:TitleProper` | mapped |
| Utenlandsk tittel | 41239 | `fiaf:TranslatedTitle` | mapped |
| Arbeidstittel | 14202 | `fiaf:WorkingTitle` | mapped |
| Alternativ tittel | 9 | `fiaf:AlternativeTitle` | mapped |
| Parallelltittel | — | `fiaf:ParallelTitle` | mapped |
| Serietittel | — | `fiaf:SeriesTitle` | mapped |
| Distribusjonstittel | — | `fiaf:AlternativeTitle` | mapped |
| Tittelvariant | 17049 | `fiaf:AlternativeTitle` | mapped |
| Alternativ skrivemåte | 5075 | `fiaf:AlternativeTitle` | mapped |
| Tittel fra annen kilde, se merknad | 1612 | `fiaf:AlternativeTitle` | mapped |
| Undertittel | 1183 | `fiaf:AlternativeTitle` | mapped |
| Omslagstittel | 371 | `fiaf:AlternativeTitle` | mapped |
| Førstelinjetittel | 106 | `fiaf:AlternativeTitle` | mapped |
| NRK-tittel | 18 | `fiaf:AlternativeTitle` | mapped |
| Opphavspersonens tittel | 9 | `fiaf:AlternativeTitle` | mapped |
| Refrengtittel | 6 | `fiaf:AlternativeTitle` | mapped |
| Konstruert tittel | 416 | `fiaf:SuppliedDevisedTitle` | mapped |

Unlisted title types fall back to `fiaf:Title` (not counted as a miss).

### 6.13 `Credits/credit.type/term` → activity `rdf:type` (CREDIT_TYPE)

| source value | observed n | target | disposition |
|---|---|---|---|
| Regissør | 11700 | `fiaf:Director` | mapped |
| Produksjonsselskap | 4475 | `fiaf:ProductionCompany` | mapped |
| Skuespiller | 26305 | `fiaf:CastMember` | mapped |
| Komponist | 1959 | `fiaf:Composer` | mapped |
| Gruppe - musikk | 126 | `fiaf:MusicPerformer` | mapped |
| Vokalist | 66 | `fiaf:MusicPerformer` | mapped |
| Fotograf (levende bilder) | 2437 | `fiaf:Cinematographer` | mapped |
| Foto - stab | 1204 | `fiaf:CinematographyActivity` | mapped |
| Klipp | 2136 | `fiaf:FilmEditor` | mapped |
| Manus | 6071 | `fiaf:Writer` | mapped |
| Litterært forelegg | 1423 | `fiaf:SourceMaterial` | mapped |
| Lyd | 2986 | `fiaf:SoundActivity` | mapped |
| Scenografi | 1814 | `fiaf:ArtDirector` | mapped |
| Sminke | 1206 | `fiaf:MakeUpArtist` | mapped |
| Kostymer | 1099 | `fiaf:CostumeDesigner` | mapped |
| Rekvisitter | 906 | `fiaf:ProductionDesignActivity` | mapped |
| Script | 716 | `fiaf:Continuity` | mapped |
| Dirigent | 51 | `fiaf:MusicConductor` | mapped |
| Produksjon/produsent | 4065 | `fiaf:Producer` | mapped |
| Produksjonsledelse/-stab | 1878 | `fiaf:ProductionManager` | mapped |
| Innspillingsledelse/-stab | 768 | `fiaf:ProductionManager` | mapped |
| Regi | — | `fiaf:Director` | mapped |
| Regissør (regi) | — | `fiaf:Director` | mapped |
| Produsent | — | `fiaf:Producer` | mapped |
| Produksjonsleder | — | `fiaf:ProductionManager` | mapped |
| Produksjonssjef | — | `fiaf:ProductionManager` | mapped |
| Utøvende produsent | — | `fiaf:ExecutiveProducer` | mapped |
| Medprodusent | — | `fiaf:Coproducer` | mapped |
| Kameramann | — | `fiaf:Cinematographer` | mapped |
| Fotograf | — | `fiaf:Cinematographer` | mapped |
| Foto | — | `fiaf:Cinematographer` | mapped |
| B-foto | — | `fiaf:CameraOperator` | mapped |
| Klipper | — | `fiaf:FilmEditor` | mapped |
| Forfatter | — | `fiaf:Writer` | mapped |
| Manusforfatter | — | `fiaf:Writer` | mapped |
| Dreiebok | — | `fiaf:Writer` | mapped |
| Forteller | — | `fiaf:Narrator` | mapped |
| Speaker | — | `fiaf:Narrator` | mapped |
| Animasjon | 199 | `fiaf:Animator` | mapped |
| Animator | — | `fiaf:Animator` | mapped |
| Scenograf | — | `fiaf:ArtDirector` | mapped |
| Produksjonsdesigner | — | `fiaf:ProductionDesigner` | mapped |
| Kostymedesigner | — | `fiaf:CostumeDesigner` | mapped |
| Kostyme | — | `fiaf:CostumeDesigner` | mapped |
| Sminkør | — | `fiaf:MakeUpArtist` | mapped |
| Maskør | — | `fiaf:MakeUpArtist` | mapped |
| Lyddesigner | — | `fiaf:SoundActivity` | mapped |
| Lydtekniker | — | `fiaf:SoundActivity` | mapped |
| Musikk | — | `fiaf:Composer` | mapped |
| Musikk (komponist) | — | `fiaf:Composer` | mapped |
| Sanger | — | `fiaf:MusicPerformer` | mapped |
| Sangerinne | — | `fiaf:MusicPerformer` | mapped |
| Distributør | — | `fiaf:Distributor` | mapped |
| Distribusjon | 2046 | `fiaf:Distributor` | mapped |
| Lys | 704 | `fiaf:GafferLighting` | mapped |
| Lyssetter | — | `fiaf:GafferLighting` | mapped |
| Rekvisitør | — | `fiaf:Activity` | mapped |
| Finansiering/sponsing | 1754 | `fiaf:ProducingActivity` | mapped |
| Annen funksjon | 1433 | `fiaf:Activity` | mapped |
| Regi - stab | 685 | `fiaf:DirectingActivity` | mapped |
| Fotograf (stillbilder) | 467 | `fiaf:CinematographyActivity` | mapped |
| Rettighetshaver | 424 | `fiaf:CopyrightandDistributionActivity` | mapped |
| Medvirkende | 318 | `fiaf:CastActivity` | mapped |
| Utgiver | 166 | `fiaf:CopyrightandDistributionActivity` | mapped |
| Tekstforfatter (musikk) | 150 | `fiaf:Lyricist` | mapped |
| Instrumentalist | 115 | `fiaf:MusicPerformer` | mapped |
| Musikalsk ansvarlig | 114 | `fiaf:MusicSupervisor` | mapped |
| Kontakt for rettighetshaver | 67 | `fiaf:CopyrightandDistributionActivity` | mapped |
| Oversettelse/bearbeidelse | 57 | `fiaf:Adaptation` | mapped |
| Redigering | 39 | `fiaf:FilmEditor` | mapped |
| Koreograf | 32 | `fiaf:Choreographer` | mapped |
| Reporter/kommentator | 28 | `fiaf:CastActivity` | mapped |
| Tegner/maler/grafiker | 27 | `fiaf:ProductionDesignActivity` | mapped |
| Musikk/tekst (uklart ansv.) | 26 | `fiaf:MusicActivity` | mapped |
| Oppdragsgiver | 23 | `fiaf:ProducingActivity` | mapped |
| Oppleser/forteller | 21 | `fiaf:Narrator` | mapped |
| Design | 19 | `fiaf:ProductionDesigner` | mapped |
| Ukjent/uklar funksjon | 15 | `fiaf:Activity` | mapped |
| Kringkaster | 13 | `fiaf:Broadcaster` | mapped |
| Programleder | 9 | `fiaf:Presenter` | mapped |
| Arrangør | 7 | `fiaf:Activity` | mapped |
| Illustratør | 7 | `fiaf:ProductionDesignActivity` | mapped |
| Emne for verket | 5 | `fiaf:Activity` | mapped |
| Kunstnerisk ansvarlig | — | `fiaf:Activity` | mapped |
| Avbildet | — | `fiaf:Activity` | mapped |
| Intervjuer | — | `fiaf:Interviewer` | mapped |
| Arkivskaper/samlingsskaper | — | `fiaf:Activity` | mapped |
| Taler | — | `fiaf:Narrator` | mapped |
| Reprofotograf | — | `fiaf:CinematographyActivity` | mapped |
| Tilknyttet verk | — | `fiaf:Activity` | mapped |
| Hovedordningsord | — | `fiaf:Activity` | mapped |
| Skaper av avbildet objekt | — | `fiaf:Activity` | mapped |

Unlisted credit types fall back to `fiaf:Activity` (not counted as a miss).

### 6.14 `Dating/dating.type` → event `rdf:type` (DATING_TYPE)

| source value | observed n | target | disposition |
|---|---|---|---|
| Produksjon | 7347 | `fiaf:ProductionEvent` | mapped |
| Innspilt | 46 | `fiaf:ProductionEvent` | mapped |
| Kinopremiere | 4239 | `fiaf:ReleaseEvent` | mapped |
| Premiere | — | `fiaf:ReleaseEvent` | mapped |
| Reprise | 3 | `fiaf:ReleaseEvent` | mapped |
| Utgitt | 4468 | `fiaf:PublicationEvent` | mapped |
| Nyutgivelse | 753 | `fiaf:PublicationEvent` | mapped |
| Katalogisert | — | `fiaf:PublicationEvent` | mapped |
| TV-premiere | — | `fiaf:BroadcastEvent` | mapped |
| Kringkastet | 170 | `fiaf:BroadcastEvent` | mapped |
| Sensurdato | 866 | `fiaf:CensorshipEvent` | mapped |
| Copyright | 16 | `fiaf:RightsCopyrightRegistrationEvent` | mapped |
| Ukjent | 3 | `fiaf:Event` | mapped |
| Created | 1 | `fiaf:Event` | mapped |

Unlisted dating types fall back to `fiaf:Event` (not counted as a miss).

### 6.15 `Language/language/term` → `fiaf:hasLanguage` (LANGUAGE)

| source value | observed n | target | disposition |
|---|---|---|---|
| Norsk | 15549 | `fiaf:Norwegian` | mapped |
| Norsk (bokmål) | — | `fiaf:Norwegian` | mapped |
| Norsk (nynorsk) | — | `fiaf:Norwegian` | mapped |
| Norsk bokmål | 33 | `fiaf:NorwegianBokmal` | mapped |
| Nynorsk | 72 | `fiaf:NorwegianNynorsk` | mapped |
| Engelsk | 4748 | `fiaf:English` | mapped |
| Tysk | 528 | `fiaf:German` | mapped |
| Fransk | 495 | `fiaf:French` | mapped |
| Svensk | 1791 | `fiaf:Swedish` | mapped |
| Dansk | 1328 | `fiaf:Danish` | mapped |
| Spansk | 306 | `fiaf:Spanish` | mapped |
| Italiensk | 139 | `fiaf:Italian` | mapped |
| Portugisisk | 49 | `fiaf:Portuguese` | mapped |
| Nederlandsk | 70 | `fiaf:Dutch` | mapped |
| Flamsk | 42 | `fiaf:Dutch` | mapped |
| Russisk | 154 | `fiaf:Russian` | mapped |
| Polsk | 68 | `fiaf:Polish` | mapped |
| Finsk | 755 | `fiaf:Finnish` | mapped |
| Islandsk | 85 | `fiaf:Icelandic` | mapped |
| Japansk | 75 | `fiaf:Japanese` | mapped |
| Kinesisk | 39 | `fiaf:Chinese` | mapped |
| Mandarin | 6 | `fiaf:Chinese` | mapped |
| Kantonesisk | — | `fiaf:Chinese` | mapped |
| Arabisk | 114 | `fiaf:Arabic` | mapped |
| Egyptisk | — | `fiaf:Arabic` | mapped |
| Hebraisk | 18 | `fiaf:Hebrew` | mapped |
| Tyrkisk | 39 | `fiaf:Turkish` | mapped |
| Hindi | 12 | `fiaf:Hindi` | mapped |
| Samisk | 101 | `fiaf:NorthernSami` | mapped |
| Nord-samisk | 9 | `fiaf:NorthernSami` | mapped |
| Koreansk | 82 | `fiaf:Korean` | mapped |
| Persisk | 47 | `fiaf:Persian` | mapped |
| Tsjekkisk | 34 | `fiaf:Czech` | mapped |
| Ungarsk | 33 | `fiaf:Hungarian` | mapped |
| Thai | 24 | `fiaf:Thai` | mapped |
| Ukrainsk | 21 | `fiaf:Ukrainian` | mapped |
| Gresk | 20 | `fiaf:Greek` | mapped |
| Urdu | 20 | `fiaf:Urdu` | mapped |
| Bosnisk | 16 | `fiaf:Bosnian` | mapped |
| Estisk | 14 | `fiaf:Estonian` | mapped |
| Georgisk | 14 | `fiaf:Georgian` | mapped |
| Serbisk | 14 | `fiaf:Serbian` | mapped |
| Kurdisk | 13 | `fiaf:Kurdish` | mapped |
| Vietnamesisk | 13 | `fiaf:Vietnamese` | mapped |
| Nepali | 12 | `fiaf:Nepali` | mapped |
| Slovensk | 12 | `fiaf:Slovenian` | mapped |
| Rumensk/moldovsk | 11 | `fiaf:Romanian` | mapped |
| Ubestemt | 10 | — | dropped (recognised, no target) |
| Grønlandsk | 9 | `fiaf:Kalaallisut` | mapped |
| Indonesisk (Bahasa Indonésia) | 9 | `fiaf:Indonesian` | mapped |
| Tibetansk | 9 | `fiaf:Tibetan` | mapped |
| Katalansk | 8 | `fiaf:Catalan` | mapped |
| Latvisk | 7 | `fiaf:Latvian` | mapped |
| Malayisk | 7 | `fiaf:Malay` | mapped |
| Bengali | — | `fiaf:Bengali` | mapped |
| Kroatisk | — | `fiaf:Croatian` | mapped |
| Somalisk | — | `fiaf:Somali` | mapped |
| Swahili | — | `fiaf:Swahili` | mapped |
| Tsjetsjensk | — | `fiaf:Chechen` | mapped |
| Walisisk | — | `fiaf:Welsh` | mapped |
| Amharisk | — | `fiaf:Amharic` | mapped |
| Flere språk | — | — | dropped (recognised, no target) |
| Dzongkha | — | `fiaf:Dzongkha` | mapped |
| Malayalam | — | `fiaf:Malayalam` | mapped |
| Albansk | — | `fiaf:Albanian` | mapped |
| Burmesisk | — | `fiaf:Burmese` | mapped |
| Gælisk | — | `fiaf:Gaelic` | mapped |
| Maltesisk | — | `fiaf:Maltese` | mapped |
| Mongolsk | — | `fiaf:Mongolian` | mapped |
| Slovakisk | — | `fiaf:Slovak` | mapped |
| Bulgarsk | — | `fiaf:Bulgarian` | mapped |
| Esperanto | — | `fiaf:Esperanto` | mapped |
| Filipino | — | `fiaf:Tagalog` | mapped |
| Tagalog | — | `fiaf:Tagalog` | mapped |
| Færøyisk | — | `fiaf:Faroese` | mapped |
| Panjabi | — | `fiaf:Punjabi` | mapped |
| Retoromansk | — | `fiaf:Romansh` | mapped |
| Tamil | — | `fiaf:Tamil` | mapped |

**Extensions:**

| source value | observed n | target | disposition |
|---|---|---|---|
| Sør-samisk | — | `nln://extension/language/sma` (`rdfs:subClassOf fiaf:Language`) | extension |
| Keltisk | — | `nln://extension/language/cel` (`rdfs:subClassOf fiaf:Language`) | extension |
| Eskimoisk-aleutisk | — | `nln://extension/language/esx` (`rdfs:subClassOf fiaf:Language`) | extension |

`Uten tale` is not a `fiaf:Language`: FIAFcore models `NoDialogue` as a
`fiaf:LanguageUsage`, so it is emitted as a usage node instead (§6.23).

### 6.16 `Dimension/dimension.unit/term` → `fiaf:hasExtent` (DIMENSION_UNIT)

| source value | observed n | target | disposition |
|---|---|---|---|
| Meter | 16446 | `fiaf:Metre` | mapped |
| meter | — | `fiaf:Metre` | mapped |
| m | — | `fiaf:Metre` | mapped |
| Fot | — | `fiaf:Foot` | mapped |
| fot | — | `fiaf:Foot` | mapped |
| foot | — | `fiaf:Foot` | mapped |
| Gram | 1790 | — | dropped (recognised, no target) |
| Bilderuter | 59 | — | dropped (recognised, no target) |

### 6.17 `item_status/term` → `fiaf:hasStatus` (ITEM_STATUS)

| source value | observed n | target | disposition |
|---|---|---|---|
| Brukseksemplar | 91194 | `fiaf:Access` | mapped |
| Kopieringseksemplar | 9610 | `fiaf:Access` | mapped |
| Overskuddseksemplar | 5161 | `fiaf:Access` | mapped |
| Originaleksemplar | 18742 | `fiaf:Preservation` | mapped |
| Originalmateriale | 16178 | `fiaf:Preservation` | mapped |
| Sikringseksemplar | 6828 | `fiaf:Preservation` | mapped |
| Sikringseksemplar (internprodusert) | 5751 | `fiaf:Preservation` | mapped |
| Sikringseksemplar (eksternprodusert) | 515 | `fiaf:Preservation` | mapped |
| Sikringseksemplar (fra NFI-basen) | 2348 | `fiaf:Preservation` | mapped |
| Nitrateksemplar-negativt | 1541 | `fiaf:Preservation` | mapped |
| Nitrateksemplar-positivt | 1247 | `fiaf:Preservation` | mapped |
| Mezzanin | 145 | `fiaf:Preservation` | mapped |
| Bevaringseksemplar (fra NFI-Mavis) | 101 | `fiaf:Preservation` | mapped |
| Frasortert materiale | 411 | — | dropped (recognised, no target) |

### 6.18 `Alternative_number/alternative_number.type/term` → identifiers (ALT_NUMBER_KEEP)

Only the alternative-number *types* below are kept, as extra
`fiaf:hasIdentifier` values (the type itself is not emitted):

| source value | observed n | target |
|---|---|---|
| (ISAN) Internat. Standard Audiovisual Number | — | `fiaf:hasIdentifier` (value only) |
| EIDR (unik verks-id for film og fjernsyn) | — | `fiaf:hasIdentifier` (value only) |
| ISBN | — | `fiaf:hasIdentifier` (value only) |
| Sensurnummer | — | `fiaf:hasIdentifier` (value only) |

### 6.19 `Description/description.type/term` → `dcterms:description` (DESCRIPTION_TYPE)

| source value | observed n | target | disposition |
|---|---|---|---|
| Beskrivelse | 6198 | `dcterms:description` | published (no language tag) |
| Norsk til publisering | 1257 | `dcterms:description` | published (lang `nb`) |
| Engelsk til publisering | 218 | `dcterms:description` | published (lang `en`) |
| Detaljert sammendrag | 14 | `dcterms:description` | published (lang `nb`) |
| Ekstern kommentar | 5 | `dcterms:description` | published (no language tag) |

Any description type **not** listed here is internal and skipped by default
(`DESCRIPTION_TYPE.get(value, False)`).

### 6.20 Organisation labels (ORGS)

| slug | label |
|---|---|
| nln | The National Library of Norway |

### 6.21 `Credits/credit.type/term` → agent kind (CREDIT_AGENT_KIND)

Agents are typed by the credit type. Any type not listed defaults to `person`.

| source value | kind | target |
|---|---|---|
| `Produksjonsselskap` | organisation | `fiaf:Organisation` |
| `Kringkaster` | organisation | `fiaf:Organisation` |
| `Utgiver` | organisation | `fiaf:Organisation` |
| `Produksjon/produsent` | generic | `fiaf:Agent` |
| `Produsent` | generic | `fiaf:Agent` |
| `Utøvende produsent` | generic | `fiaf:Agent` |
| `Medprodusent` | generic | `fiaf:Agent` |
| `Distribusjon` | generic | `fiaf:Agent` |
| `Distributør` | generic | `fiaf:Agent` |
| `Oppdragsgiver` | generic | `fiaf:Agent` |
| _(anything else)_ | person | `fiaf:Person` |

The agent **node** is emitted once per priref (first credit wins); every activity
still links `fiaf:hasAgent` to it.

### 6.22 `Stock/stock/term` → `fiaf:hasStock` (STOCK)

One stock node `nln://resource/stock/{priref}/{n}` per `<Stock>` group, typed by
manufacturer, with `rdfs:label` and `fiaf:hasStockCode` from
`stock_formulation`/`stock_batch_no`.

| source value | target | disposition |
|---|---|---|
| Kodak | `fiaf:Kodak` | mapped |
| Sony | `fiaf:Sony` | mapped |
| Gevaert | `fiaf:Gevaert` | mapped |
| Agfa | `fiaf:Agfa` | mapped |
| Ilford | `fiaf:Ilford` | mapped |
| Agfa Gevaert | `fiaf:AgfaGevaert` | mapped |
| Orwo | `fiaf:Orwo` | mapped |
| Eastman | `fiaf:Eastman` | mapped |
| Fuji | `fiaf:Fuji` | mapped |
| Maxell, BASF, Scotch, TDK, Ulike fabrikater blandet | `fiaf:Stock` | generic (brand kept as `rdfs:label`) |

Undeclared brands are **not** coverage misses; they are tracked in
[`ONTOLOGY_GAPS.md`](ONTOLOGY_GAPS.md) as missing `Stock` subclasses.

### 6.23 `Language/language.usage/term` → usage node type (LANGUAGE_USAGE)

`fiaf:hasLanguageUsage` → `LanguageUsage`; `Dialogue` (⊃ `SpokenLanguage`) vs
`WrittenLanguage` (⊃ `Subtitles`). Default `SpokenLanguage`. A `language/term`
of `Uten tale` overrides the usage class with `fiaf:NoDialogue` and emits no
`hasLanguage`.

| source value | target | disposition |
|---|---|---|
| `language/term` = `Uten tale` | `fiaf:NoDialogue` | mapped as usage (no `hasLanguage`) |
| Originalspråk | `fiaf:SpokenLanguage` | mapped |
| Dubbing | `fiaf:SpokenLanguage` | mapped |
| Synstolking | `fiaf:SpokenLanguage` | mapped |
| Versjonering | `fiaf:SpokenLanguage` | mapped |
| Undertekster | `fiaf:Subtitles` | mapped |
| Teksting for hørselshemmede | `fiaf:Subtitles` | mapped |
| Tekstplakater/mellomtekster | `fiaf:WrittenLanguage` | mapped |
| Tekstelementer | `fiaf:WrittenLanguage` | mapped |

`Title/title.language/term` is mapped to a BCP-47 tag via `LANGUAGE_TAG`
(`Norsk` → `no`, `Engelsk` → `en`, …) and used to language-tag the title literal.

## 7. Defaults and fallbacks

| field | fallback target |
|---|---|
| `Title/title.type/term` | `fiaf:Title` |
| `Credits/credit.type/term` | `fiaf:Activity` |
| `Dating/dating.type` | `fiaf:Event` |
| `manifestation_type/term` | `fiaf:Manifestation` |

A fallback target is emitted whenever the field is empty or the value is
unlisted. An **unlisted** (non-empty) value is nevertheless still recorded as
a coverage miss (§9), so `--strict` will flag it; empty fields are not misses.

## 8. Tuning surface

Recognised values that currently produce **no** FIAFcore target (`dropped`
above) — the first place to look when fine-tuning:

- `colour_type` → `Ingen`
- `colour_type` → `Annet, se merknad`
- `content.genre` → `Fjernsynsfilm`
- `content.genre` → `Dokumentarfilm`
- `content.genre` → `Underholdning`
- `content.genre` → `Reklame`
- `content.genre` → `W - Pop og rock`
- `gauge` → `Annet, se merknad`
- `material` → `Papir`
- `material` → `Annet`
- `material` → `Ukjent`
- `material` → `Plast`
- `material` → `Glass`
- `broadcast_standard` → `HD`
- `broadcast_standard` → `REGB`
- `sound_system` → `Mono`
- `sound_system` → `Dolby Mono`
- `sound_system` → `Annet, se merknad`
- `language` → `Ubestemt`
- `language` → `Flere språk`
- `dimension.unit` → `Gram`
- `dimension.unit` → `Bilderuter`
- `item_status` → `Frasortert materiale`
- `carrier_type_specific` → `Ark (løse)`
- `carrier_type_specific` → `Fotografisk papir`
- `carrier_type_specific` → `Heftet`
- `carrier_type_specific` → `Mappe`
- `carrier_type_specific` → `Innbundet`
- `carrier_type_specific` → `Blad`
- `carrier_type_specific` → `Kartong, brettet`
- `carrier_type_specific` → `Diapositiv`
- `carrier_type_specific` → `Produksjonsmateriale`
- `carrier_type_specific` → `Arbeidskopi`
- `carrier_type_specific` → `Annet`
- `carrier_type_specific` → `Ukjent`
- `carrier_type_specific` → `Blandet`
- `carrier_type_specific` → `Omvender`
- `carrier_type_specific` → `Tekster`
- `carrier_type_specific` → `MC-kassetter`
- `carrier_type_specific` → `DTS (digital theatrical system)`

NLN extension classes (no FIAFcore concept; add a FIAFcore class if one appears):

- country `Sovjetunionen` → `nln://extension/iso3166-3/SU`
- country `Jugoslavia` → `nln://extension/iso3166-3/YU`
- gauge `28mm` → `nln://extension/format/28mmFilm`
- language `Sør-samisk` → `nln://extension/language/sma`
- language `Keltisk` → `nln://extension/language/cel`
- language `Eskimoisk-aleutisk` → `nln://extension/language/esx`

Fields that are **not** mapped at all:

- Condition, treatment and loan data (not published).
- Internal description types (see §6.19).
- Deferred-interest fields tracked by `scan.py` but not emitted (the
  `HISTOGRAM_EXTRA` paths, e.g. `Object_category/object_category/term`,
  `Medium/medium/term`, `Submedium/submedium/term`, `aspect_ratio/term`,
  `film_type/value`, `format/value`, `carrier_size/term`, `frame_rate/term`,
  `preferred_environment/term`, `Collection/collection.name/collection`,
  `location/default.name/name`, `Free_field/free_field.type/term`,
  `Verification/verification.notes`, `project/term`, `Object_name/object_name/term`).

Fields that are **wanted but currently unmappable** because FIAFcore has no
home for them (kept in the XML bundles; see [`ONTOLOGY_GAPS.md`](ONTOLOGY_GAPS.md)):
`colour_system`, `aspect_ratio`, `frame_rate`, `carrier_size`, `Collection`,
storage/`preferred_environment`/locations, `UseRestriction`/rights,
condition/quality, the digital technical set, `Person` birth/death,
`credit.principal_role`/`credit.on_screen`, `stock_year`/`stock_country`,
and the missing `Stock` subclasses (`Maxell`, `BASF`, `Scotch`, `TDK`).

## 9. Coverage semantics

- `Vocab._lookup` returns the mapped class, or the default (`None` unless a
  fallback is set) and records a **coverage miss** when the value is missing
  from the table.
- `Vocab._lookup_list` returns a list (`[]` for no target) and likewise
  records a miss for unlisted values.
- A value that *is* in a table but maps to `None`/`[]`/`ignore` is
  **recognised** and is **not** a miss.
- `transform.py --strict` exits non-zero if any miss is recorded; the
  `coverage-report`/`--merged` run prints the miss count.

## 10. XSLT parity

`nln.xsl` is an XSLT 1.0 port generated from the same tables; after changing
`nb_fiafcore/tables.py`, regenerate it with:

```bash
python3 scripts/gen_xslt.py
```

`tests/test_xslt.py` checks that the Python transform and `nln.xsl` produce
isomorphic graphs over the sample bundle.
