# /// script
# requires-python = ">=3.13"
# dependencies = ["rdflib", "lxml"]
# ///
"""Run from the repository root: uv run scripts/check_taxonomy_review.py.

Synthetic regression checks; archive source datasets are not required.
"""

from pathlib import Path
import re

from lxml import etree
from rdflib import Graph, Namespace, RDF, RDFS, OWL, XSD, Literal, URIRef
from rdflib.compare import isomorphic
from rdflib.namespace import DCTERMS


F = Namespace("https://dev.fiafcore.org/")
BA = "http://www.bundesarchiv.de/schemas/de-barch/fw-view-1.0"
ontology = Graph()
for path in Path("ontology").glob("*.ttl"):
    ontology.parse(path)


def transform(path, xml):
    result = etree.XSLT(etree.parse(str(path)))(etree.fromstring(xml.encode()))
    return Graph().parse(data=etree.tostring(result), format="xml")


items = Path("transform/bfi/xsl/BFI_FIAF_LOD_Items.xsl")
manifestations = Path("transform/bfi/xsl/BFI_FIAF_LOD_Manifestations.xsl")
bundesarchiv = Path("transform/bundesarchiv/xsl/bundesarchiv.xsl")


def bfi_item(description="", stock="", base=""):
    root = etree.Element("record", priref="check")
    if description:
        etree.SubElement(root, "physical_description").text = description
    if stock:
        etree.SubElement(etree.SubElement(root, "stock"), "stock_film").text = stock
    if base:
        etree.SubElement(etree.SubElement(root, "base"), "value", lang="0").text = base
    return transform(items, etree.tostring(root).decode())


def ba_item(material="", code="", container="", gauge=""):
    return transform(bundesarchiv, f'''<root xmlns:ba="{BA}">
        <ba:Exemplar uuid="check">
            {f'<ba:Container>{container}</ba:Container>' if container else ''}
            {f'<ba:Filmbreite>{gauge}</ba:Filmbreite>' if gauge else ''}
            <ba:Aufbewahrungseinheit uuid="part">
                {f'<ba:Materialart>{material}</ba:Materialart>' if material else ''}
                {f'<ba:Rohfilmtyp>{code}</ba:Rohfilmtyp>' if code else ''}
            </ba:Aufbewahrungseinheit>
        </ba:Exemplar></root>''')


for child, parent in [("Hi8", "VideoTape"), ("SuperVHS", "VideoTape"),
                      ("DVCPROHD", "DV"), ("UltraHDBluRay", "VideoDisc"),
                      ("ProfessionalDisc", "VideoDisc"), ("VideoTape", "VideoFormat"),
                      ("VideoDisc", "VideoFormat"), ("OpenReelAudiotape", "AudioTape"),
                      ("CD", "AudioDisc"), ("QuarterInchAudiotape", "OpenReelAudiotape"),
                      ("QuerterInchAudiotape", "OpenReelAudiotape"),
                      ("MagneticFilm", "FilmFormat"), ("35mmMagneticFilm", "MagneticFilm"),
                      ("16mmMagneticFilm", "MagneticFilm"),
                      # Phase 0 Element decisions.
                      ("FilmSoundElement", "FilmElement"), ("SoundNegative", "FilmSoundElement"),
                      ("SoundPositive", "FilmSoundElement"),
                      ("SeparatedMagneticSound", "FilmSoundElement"),
                      ("OriginalCutNegative", "OriginalNegative"), ("FilmOutNegative", "Negative"),
                      ("OriginalReversalPositive", "ReversalPositive"),
                      ("OriginalSoundRecording", "AudioElement"),
                      ("HomeVideoRelease", "VideoElement"),
                      ("OriginalDigitalRecording", "DigitalElement"),
                      ("DigitalRelease", "DigitalElement"),
                      # Phase 1 Sound decisions.
                      ("Mute", "Sound"), ("Silent", "SoundCharacteristic"),
                      ("AnalogueOpticalSound", "SoundStandard"),
                      ("OpticalVariableArea", "AnalogueOpticalSound"),
                      ("OpticalVariableDensity", "AnalogueOpticalSound"),
                      ("AnalogueDiscSound", "SoundStandard"),
                      ("DolbyDigitalPlus", "AudioCodec"), ("DolbyTrueHD", "AudioCodec"),
                      ("DTSHD", "AudioCodec"),
                      # Phase 1 Colour decisions.
                      ("Warnercolor", "Eastmancolor"), ("DeLuxe", "Eastmancolor"),
                      ("Duartcolor", "Eastmancolor"), ("Metrocolor", "Eastmancolor"),
                      ("Supercinecolor", "SubtractiveColourProcess"),
                      # Phase 1 LanguageUsage decision.
                      ("Narration", "SpokenLanguage"), ("AudioDescription", "SpokenLanguage"),
                      ("NoDialogue", "Dialogue"),
                      # Phase 1 Extent decision.
                      ("Length", "Extent"), ("Foot", "Length"), ("Metre", "Length"),
                      ("Byte", "Extent"), ("Minute", "Duration"),
                      ("Reel", "Extent"),
                      # Phase 1 Event decision.
                      ("AccessionEvent", "Event"), ("DeAcquisitionEvent", "Event"),
                      ("OutgoingLoanEvent", "Event"), ("LegalDepositEvent", "AcquisitionEvent"),
                      ("LoanEvent", "Event"),
                      ("TheatricalDistributionEvent", "DistributionEvent"),
                      ("NonTheatricalDistributionEvent", "DistributionEvent")]:
    assert list(ontology.objects(F[child], RDFS.subClassOf)) == [F[parent]], child
assert (F.hasExtentValue, RDFS.range, XSD.decimal) in ontology
for legacy_unit in [F.Kilobyte, F.Megabyte, F.Gigabyte, F.Terabyte]:
    assert (legacy_unit, OWL.deprecated, Literal(True)) in ontology
    assert (legacy_unit, RDFS.subClassOf, F.Extent) in ontology

extent_graph = transform(bundesarchiv, f'''<root xmlns:ba="{BA}">
    <ba:Manifestation uuid="extent"><ba:Laufzeit>12,5</ba:Laufzeit><ba:Gesamtlaenge>42.25</ba:Gesamtlaenge></ba:Manifestation>
    <ba:Exemplar uuid="extent"><ba:Laenge>0</ba:Laenge><ba:Laenge> </ba:Laenge></ba:Exemplar>
</root>''')
for subject, unit, value in [
    ("bundesarchiv://resource/manifestation/extent", F.Minute, "12.5"),
    ("bundesarchiv://resource/manifestation/extent", F.Metre, "42.25"),
    ("bundesarchiv://resource/item/extent", F.Metre, "0"),
]:
    assert any(
        (node, RDF.type, unit) in extent_graph
        and (node, F.hasExtentValue, Literal(value, datatype=XSD.decimal)) in extent_graph
        for node in extent_graph.objects(URIRef(subject), F.hasExtent)
    )
assert len(list(extent_graph.objects(None, F.hasExtentValue))) == 3

for removed in ["OpticalVideoDisc", "HomeViewingCopy", "OpticalSoundProcess",
                "DirectPositive", "ChromolyticSingleLayer", "ColourSeparation",
                "InstantDyeDiffusion"]:
    assert not list(ontology.triples((F[removed], None, None))), removed
assert (F.QuerterInchAudiotape, OWL.deprecated, Literal(True)) in ontology
assert (F.QuerterInchAudiotape, DCTERMS.isReplacedBy, F.QuarterInchAudiotape) in ontology
for term in ["hasAchievement", "hasAwardName", "hasDate", "nominationOnly",
             "hasVerdict", "hasIdentifierValue"]:
    assert (F[term], RDF.type, OWL.DatatypeProperty) in ontology
    assert (F[term], RDF.type, OWL.ObjectProperty) not in ontology

# Generic positives preserve their independent colour/process description.
for description in ["Positive", "BW Positive", "Original Positive", "Tinted Positive",
                    "Original / Dupe Positive", "Colour Positive", "Toned Positive"]:
    graph = bfi_item(description)
    assert (None, F.isElement, F.Positive) in graph, description
    assert (None, F.isElement, F.ReleasePrint) not in graph
graph = bfi_item("Tinted Positive")
assert (None, F.hasColourProcess, F.Tinted) in graph
assert (None, RDF.type, F.Colour) not in graph
assert (None, RDF.type, F.BlackAndWhite) not in graph

for description in ["Magnetic", "Magnetic recording", "Dupe Magnetic Recording",
                    "Magnetic Recording Loop", "Magnetic Recording 3 Track Stereophonic",
                    "Master Magnetic Recording"]:
    graph = bfi_item(description)
    expected = F.AudioMaster if description.startswith("Master") else F.AudioElement
    assert (None, F.isElement, expected) in graph
    assert (None, F.hasSoundStandard, F.Magnetic) in graph
    assert (None, F.isElement, F.SeparatedMagneticSound) not in graph
    assert (None, F.hasFormat, F.OpenReelAudiotape) not in graph

brands = ["Ampex", "Ansco", "Deko", "EMTEC", "Goerz-Tenax", "Indu", "JVC",
          "Lignose", "Mafe", "Memorex", "Perutz", "Pyral", "Sakura", "Svema", "Zonal"]
for brand in brands + ["SONY", "Kodak Canada", "Kodak France", "Pathe Freres", "Kodak"]:
    graph = bfi_item(stock=brand)
    nodes = list(graph.objects(None, F.hasStock))
    assert len(nodes) == 1, brand
    term = graph.value(nodes[0], RDF.type)
    assert (term, RDF.type, OWL.Class) in ontology, (brand, term)
for brand in ["Unmarked", "Cbema", "SVMA", "unknown credit activity"]:
    assert not list(bfi_item(stock=brand).objects(None, F.hasStock)), brand
assert (None, F.hasBase, F.PVCBase) in bfi_item(base="PVC")

for material, term in {"High 8/8mm": "VideoFormat", "D 1 oder 2": "VideoFormat",
                       "BETA": "VideoFormat", "MAZ": "VideoFormat", "AMPEX DCT": "AmpexDCT",
                       "XDCAM PFD 50DLA": "ProfessionalDisc", "FILE": "DigitalFormat"}.items():
    assert (None, F.hasFormat, F[term]) in ba_item(material), material
for container in ["", "Unbekannt", "OHNE Container"]:
    assert (None, F.hasFormat, F.DigitalFormat) in ba_item("FILE", container=container)
assert (None, F.hasFormat, F.DigitalFormat) not in ba_item("FILE", container="MXF")
assert (None, F.hasFormat, F.MXF) in ba_item("FILE", container="MXF")

# Mute is valid for digital objects (optional) and at Manifestation level (FIAF manual #570).
mute = str(ontology.value(F.Mute, DCTERMS.description) or
           ontology.value(F.Mute, Namespace("http://purl.org/dc/elements/1.1/").description))
assert "Not used for digital objects" not in mute and "picture-only scan" in mute

for material in ["Stumme_Kopie_mit_Tonkasch", "Stummes_Duplikatnegativ_mit_Tonkasch",
                 "Stummes_Internegativ_mit_Tonkasch", "Stummes_Duplikatpositiv_mit_Tonkasch"]:
    graph = ba_item(material)
    assert (None, RDF.type, F.Mute) in graph
    assert (None, RDF.type, F.Silent) not in graph
assert (None, RDF.type, F.Silent) in ba_item("Stummes_Internegativ")
for gauge, element in [("35 mm", F.SeparatedMagneticSound), ("6,25 mm", F.AudioElement)]:
    assert (None, F.isElement, element) in ba_item("Magnetband", gauge=gauge)

for manufacturer, codes in {"Orwo": ["DP_31", "DN_21", "PF2", "PF2_V2", "TF_12d"],
                            "Kodak": ["2374", "2234", "2366"],
                            "Agfa": ["ST_8", "CP_30"]}.items():
    for code in codes:
        graph = ba_item(code=code)
        node = next(graph.objects(None, F.hasStock))
        assert (node, RDF.type, F[manufacturer]) in graph
        assert (node, F.hasStockCode, Literal(code)) in graph
    graph = ba_item(code=manufacturer)
    node = next(graph.objects(None, F.hasStock))
    assert node != F[manufacturer]
    assert (node, RDF.type, F[manufacturer]) in graph

# Exercise each credit label in both organisation and person branches.
for kind in ["Koerperschaft", "Person"]:
    for role in sorted(set(re.findall(r'\$funktion = \'([^\']+)\'', bundesarchiv.read_text()))):
        xml = f'''<root xmlns:ba="{BA}"><ba:Filmwerk uuid="work"><ba:Credit>
            <ba:{kind} uuid="agent"><ba:Funktion Funktion="{role}" /></ba:{kind}>
            </ba:Credit></ba:Filmwerk></root>'''
        # Not all roles exist in both source picklists; test those that do.
        tree = etree.parse(str(bundesarchiv))
        ns = {"xsl": "http://www.w3.org/1999/XSL/Transform"}
        blocks = tree.xpath(f'//xsl:for-each[@select="ba:Credit/ba:{kind}"]', namespaces=ns)
        if not blocks or not any(w.get("test") == f"$funktion = '{role}'"
                                 for w in blocks[0].xpath('.//xsl:when', namespaces=ns)):
            continue
        graph = transform(bundesarchiv, xml)
        for activity in graph.objects(None, F.hasActivity):
            assert (graph.value(activity, RDF.type), RDF.type, OWL.Class) in ontology

def ba_credit(kind, role):
    xml = f'''<root xmlns:ba="{BA}"><ba:Filmwerk uuid="work"><ba:Credit>
        <ba:{kind} uuid="agent"><ba:Funktion Funktion="{role}" /></ba:{kind}>
        </ba:Credit></ba:Filmwerk></root>'''
    graph = transform(bundesarchiv, xml)
    return {graph.value(activity, RDF.type) for activity in graph.objects(None, F.hasActivity)}

# Final credit decisions: broad organisation domains, precise person roles.
for kind, role, expected in [
    ("Koerperschaft", "Drehbuch", F.WritingActivity),
    ("Koerperschaft", "Fachberatung", F.Advisor),
    ("Koerperschaft", "Produzent", F.ProductionCompany),
    ("Koerperschaft", "Regie / Spielleitung / Realisation", F.DirectingActivity),
    ("Koerperschaft", "Kamera/Bild/Bildgestaltung/Fotografie", F.CinematographyActivity),
    ("Koerperschaft", "Synchronregie", F.SoundActivity),
    ("Koerperschaft", "Tonmischung/Mischton", F.SoundActivity),
    ("Person", "Drehbuch", F.WritingActivity),
    ("Person", "Fachberatung", F.Advisor),
    ("Person", "Szenenbild (Filmarchitekt / Bühnenbildner)", F.ProductionDesignActivity),
    ("Person", "Synchronmitwirkende", F.Activity),
]:
    assert expected in ba_credit(kind, role), (kind, role, expected)

for value, expected in [("Phase Alternate Line (PAL)", F.PAL), ("65mm film", F["65mmFilm"]),
                        ("Reel to reel tape", F.OpenReelAudiotape)]:
    graph = transform(manifestations, f'<record priref="check"><format_low_level>{value}</format_low_level></record>')
    predicate = F.hasBroadcastStandard if expected == F.PAL else F.hasFormat
    assert (None, predicate, expected) in graph
graph = transform(manifestations, '<record priref="check"><sound_system_manifestation>Surround Stereo</sound_system_manifestation></record>')
assert (None, F.hasSoundChannelConfiguration, F.Surround) in graph
assert (None, F.hasSoundChannelConfiguration, F.Stereo) not in graph

# Streams can describe the ideal Manifestation as well as actual holdings.
from rdflib.collection import Collection
stream_domain = ontology.value(F.hasStream, RDFS.domain)
assert set(Collection(ontology, ontology.value(stream_domain, OWL.unionOf))) == {
    F.Manifestation, F.Item, F.Carrier
}
for value, codec, container in [
    ("Apple ProRes 422 HQ", F.ProRes422HQ, None),
    ("ProRes QuickTime", F.ProRes, F.Quicktime),
]:
    graph = transform(manifestations, f'<record priref="check"><format_low_level>{value}</format_low_level></record>')
    manifestation = next(graph.subjects(RDF.type, F.Manifestation))
    streams = list(graph.objects(manifestation, F.hasStream))
    assert len(streams) == 1, value
    assert (streams[0], RDF.type, F.VideoStream) in graph
    assert (streams[0], F.hasVideoCodec, codec) in graph
    assert set(graph.objects(manifestation, F.hasFormat)) == ({container} if container else set())
    assert not list(graph.objects(streams[0], F.hasAudioCodec))

# Bundesarchiv uses the current tape term and keeps codecs off hasFormat.
graph = ba_item("Magnetband", gauge="6,25 mm")
assert (None, F.hasFormat, F.QuarterInchAudiotape) in graph
assert (None, F.hasFormat, F.QuerterInchAudiotape) not in graph

graph = ba_item("FILE", container="MPEG-2")
item = next(graph.subjects(RDF.type, F.Item))
streams = list(graph.objects(item, F.hasStream))
assert len(streams) == 1
assert (streams[0], RDF.type, F.VideoStream) in graph
assert (streams[0], F.hasVideoCodec, F.MPEG2) in graph
assert (None, F.hasFormat, F.MPEG2) not in graph
assert not list(graph.objects(streams[0], F.hasAudioCodec))

# Applied colour has an appearance type, with plain B&W sections kept separate.
for description, processes in [
    ("Tinted Positive", {F.Tinted}),
    ("Toned Positive", {F.Toned}),
    ("Sepia BW Positive", {F.Toned}),
    ("Tinted and Stencil Positive", {F.Tinted, F.StencilColouring}),
    ("Tinted and Toned Positive", {F.Tinted, F.Toned}),
    ("BW Tinted Positive", {F.Tinted}),
]:
    graph = bfi_item(description)
    nodes = list(graph.objects(None, F.hasColourCharacteristic))
    assert len(nodes) == 1, description
    assert set(graph.objects(nodes[0], RDF.type)) == {F.BlackAndWhiteWithAppliedColour}
    assert set(graph.objects(nodes[0], F.hasColourProcess)) == processes

graph = bfi_item("BW and Tinted Positive")
nodes = list(graph.objects(None, F.hasColourCharacteristic))
assert len(nodes) == 2
plain = next(n for n in nodes if (n, RDF.type, F.BlackAndWhite) in graph)
applied = next(n for n in nodes if (n, RDF.type, F.BlackAndWhiteWithAppliedColour) in graph)
assert not list(graph.objects(plain, F.hasColourProcess))
assert (applied, F.hasColourProcess, F.Tinted) in graph

for source, processes in [
    ("Virage", {F.Tinted}), ("Tonung", {F.Toned}),
    ("Virage und Tonung", {F.Tinted, F.Toned}),
    ("Schablonenkolorierung", {F.StencilColouring}),
    ("Handkolorierung", {F.HandColouring}),
]:
    graph = transform(bundesarchiv, f'<root xmlns:ba="{BA}"><ba:Exemplar uuid="check"><ba:Aufbewahrungseinheit uuid="part"><ba:Farbe>{source}</ba:Farbe></ba:Aufbewahrungseinheit></ba:Exemplar></root>')
    node = next(graph.objects(None, F.hasColourCharacteristic))
    assert set(graph.objects(node, RDF.type)) == {F.BlackAndWhiteWithAppliedColour}, source
    assert set(graph.objects(node, F.hasColourProcess)) == processes

for colour_xml in [
    '<colour_manifestation><value lang="0">Sepia</value></colour_manifestation>',
    '<colour_code_manifestation>Sepia</colour_code_manifestation>',
    '<colour_manifestation><value lang="0">Black and White</value></colour_manifestation><colour_code_manifestation>Sepia</colour_code_manifestation>',
]:
    graph = transform(manifestations, f'<record priref="check">{colour_xml}</record>')
    node = next(graph.objects(None, F.hasColourCharacteristic))
    assert set(graph.objects(node, RDF.type)) == {F.BlackAndWhiteWithAppliedColour}
    assert (node, F.hasColourProcess, F.Toned) in graph

# Repeated sound descriptions survive in either order; compound facets stay together.
for values in [("Dolby Stereo SR", "SDDS"), ("SDDS", "Dolby Stereo SR"), ("Mono", "SDDS")]:
    xml = ''.join(f'<sound_system_manifestation>{value}</sound_system_manifestation>' for value in values)
    graph = transform(manifestations, f'<record priref="check">{xml}</record>')
    nodes = list(graph.objects(None, F.hasSoundCharacteristic))
    assert len(nodes) == 2
    sdds = next(n for n in nodes if (n, F.hasSoundStandard, F.SDDS) in graph)
    assert not list(graph.objects(sdds, F.hasNoiseReduction))
    assert not list(graph.objects(sdds, F.hasSoundChannelConfiguration))
    other = next(n for n in nodes if n != sdds)
    if "Dolby Stereo SR" in values:
        assert (other, F.hasSoundStandard, F.DolbyStereo) in graph
        assert (other, F.hasNoiseReduction, F.DolbySR) in graph
    else:
        assert (other, F.hasSoundChannelConfiguration, F.Mono) in graph

for value in ["Sound", "Silent", "Mute"]:
    graph = transform(manifestations, f'<record priref="check"><sound_manifestation><value lang="0">{value}</value></sound_manifestation></record>')
    nodes = list(graph.objects(None, F.hasSoundCharacteristic))
    assert len(nodes) == 1
    assert (nodes[0], RDF.type, F[value]) in graph

# Unresolved colour names do not emit empty nodes, but retain known appearance.
for value in ["Scope Colour", "Image Transform", "Perfect", "", "   "]:
    xml = f'<colour_code_manifestation>{value}</colour_code_manifestation>'
    graph = transform(manifestations, f'<record priref="check">{xml}</record>')
    assert not list(graph.objects(None, F.hasColourCharacteristic)), value
    graph = transform(manifestations, f'<record priref="check">{xml}<colour_manifestation><value lang="0">Colour</value></colour_manifestation></record>')
    nodes = list(graph.objects(None, F.hasColourCharacteristic))
    assert len(nodes) == 1
    assert (nodes[0], RDF.type, F.Colour) in graph
    assert not list(graph.objects(nodes[0], F.hasColourProcess))
try:
    transform(manifestations, '<record priref="check"><colour_code_manifestation>Unrecognised test process</colour_code_manifestation></record>')
except etree.XSLTApplyError:
    pass
else:
    raise AssertionError("Unexpected colour processes must still raise an error")

# Mixed Bundesarchiv units retain every summary value and their own formats.
def ba_units(units, gauge="", container=""):
    fields = (f'<ba:Filmbreite>{gauge}</ba:Filmbreite>' if gauge else '')
    fields += (f'<ba:Container>{container}</ba:Container>' if container else '')
    return transform(bundesarchiv, f'<root xmlns:ba="{BA}"><ba:Exemplar uuid="mixed">{fields}{"".join(units)}</ba:Exemplar></root>')

item = URIRef("bundesarchiv://resource/item/mixed")
picture = URIRef("bundesarchiv://resource/carrier/picture")
magnetic = URIRef("bundesarchiv://resource/carrier/magnetic")
units = [
    '<ba:Aufbewahrungseinheit uuid="picture"><ba:Materialart>Originalbildnegativ</ba:Materialart><ba:Farbe>schwarz-weiß</ba:Farbe><ba:Traeger>Zellulosenitrat</ba:Traeger><ba:Rohfilmtyp>2374</ba:Rohfilmtyp></ba:Aufbewahrungseinheit>',
    '<ba:Aufbewahrungseinheit uuid="magnetic"><ba:Materialart>Magnetband</ba:Materialart><ba:Farbe>Farbe</ba:Farbe><ba:Traeger>Acetatcellulose</ba:Traeger><ba:Rohfilmtyp>DP 31</ba:Rohfilmtyp></ba:Aufbewahrungseinheit>',
]
graph = ba_units(units, gauge="35 mm")
assert isomorphic(graph, ba_units(list(reversed(units)), gauge="35 mm"))
assert set(graph.objects(item, F.hasBase)) == {F.NitrateBase, F.AcetateBase}
assert set(graph.objects(item, F.isElement)) == {F.OriginalNegative, F.SeparatedMagneticSound}
appearances = {graph.value(n, RDF.type) for n in graph.objects(item, F.hasColourCharacteristic)}
assert appearances == {F.BlackAndWhite, F.Colour}
stock = {(graph.value(n, RDF.type), graph.value(n, F.hasStockCode)) for n in graph.objects(item, F.hasStock)}
assert stock == {(F.Kodak, Literal("2374")), (F.Orwo, Literal("DP 31"))}
assert (None, RDF.type, F.Mute) in graph
assert (None, F.hasSoundStandard, F.Magnetic) in graph
assert set(graph.objects(item, F.hasFormat)) == {F["35mmFilm"]}
assert set(graph.objects(magnetic, F.hasFormat)) == {F["35mmMagneticFilm"]}
assert (picture, F.hasFormat, F["35mmMagneticFilm"]) not in graph
for carrier in graph.objects(item, F.hasCarrier):
    for predicate in [F.hasBase, F.hasStock, F.isElement, F.hasColourCharacteristic, F.hasSoundCharacteristic]:
        assert not list(graph.objects(carrier, predicate)), predicate

# Material formats belong to their specific units, not the Item or siblings.
units = [
    '<ba:Aufbewahrungseinheit uuid="vhs"><ba:Materialart>VHS</ba:Materialart></ba:Aufbewahrungseinheit>',
    '<ba:Aufbewahrungseinheit uuid="dvd"><ba:Materialart>DVD</ba:Materialart></ba:Aufbewahrungseinheit>',
]
graph = ba_units(units, container="MXF")
assert isomorphic(graph, ba_units(list(reversed(units)), container="MXF"))
assert set(graph.objects(item, F.hasFormat)) == {F.MXF}
assert set(graph.objects(URIRef("bundesarchiv://resource/carrier/vhs"), F.hasFormat)) == {F.VHS}
assert set(graph.objects(URIRef("bundesarchiv://resource/carrier/dvd"), F.hasFormat)) == {F.DVD}

# Explicit unit gauge overrides the Exemplar gauge for magnetic interpretation.
units = [
    '<ba:Aufbewahrungseinheit uuid="tape"><ba:Materialart>Magnetband</ba:Materialart><ba:Filmbreite>6,25 mm</ba:Filmbreite></ba:Aufbewahrungseinheit>',
    '<ba:Aufbewahrungseinheit uuid="magnetic"><ba:Materialart>Magnetband</ba:Materialart><ba:Filmbreite>16 mm</ba:Filmbreite></ba:Aufbewahrungseinheit>',
]
graph = ba_units(units, gauge="35 mm")
assert isomorphic(graph, ba_units(list(reversed(units)), gauge="35 mm"))
assert set(graph.objects(item, F.isElement)) == {F.AudioElement, F.SeparatedMagneticSound}
assert set(graph.objects(URIRef("bundesarchiv://resource/carrier/tape"), F.hasFormat)) == {F.QuarterInchAudiotape}
assert set(graph.objects(magnetic, F.hasFormat)) == {F["16mmMagneticFilm"]}

print("Taxonomy review regression checks passed.")
