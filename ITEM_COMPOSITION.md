# Proposal: Item Composition in Place of `Carrier`

**Status: proposal for discussion.** The `carrier-discussion` branch implements
it so that it can be examined against real data. It is not an adopted change to
FIAFcore.

The proposal is to stop using a separate `Carrier` level below `Item`. Every
discrete physical or digital unit would be described as an `Item`. Where a copy
consists of several units, a group `Item` would be related to its unit `Item`s
with `fiaf:hasComponent`.

This document sets out the reasoning, the drawbacks, and what remains open. The
discussion that led here, including the alternatives considered, is in
`CARRIER_AND_DIGITAL_MODELING.md`.

## 1. What is proposed

| Term | Proposed change |
| :--- | :--- |
| `fiaf:hasComponent` | New. Relates an Item to an Item that is one of the discrete units it is made up of. Domain and range are both `Item`. |
| `fiaf:Carrier` | Deprecated. Replaced by `Item`. The IRI remains. |
| `fiaf:hasCarrier` | Deprecated. Replaced by `hasComponent`. The IRI remains. |

`Carrier` would still be named in the domains of `hasFormat`, `hasEvent`,
`hasIdentifier`, and `hasStream`, so data that uses the deprecated class stays
coherent. Nothing else is added: there is no inverse property, no property for
component order, and no relation for storage, copying, or package dependency.

```text
Today                                        Proposed

Manifestation                                Manifestation
 └─ hasItem ─► Item                           └─ hasItem ─► Item
                └─ hasCarrier ─► Carrier                     └─ hasComponent ─► Item
                                                                (only when there are
                   always two levels                             several units)
```

## 2. The case for the change

### 2.1 `Carrier` cannot describe the thing it stands for

`Carrier` is defined as the discrete unit on which the moving image is
retained: the reel, the cassette, the file. That is the object an archive
actually handles. Yet it accepts only an identifier, an event, a format, and a
stream. Everything else is reserved for `Item`.

```text
                    Item          Carrier
hasIdentifier        ✓               ✓
hasEvent             ✓               ✓
hasFormat            ✓               ✓
hasStream            ✓               ✓
hasBase              ✓               ✗
hasStock             ✓               ✗
hasExtent            ✓               ✗
hasColourChar.       ✓               ✗
hasSoundChar.        ✓               ✗
hasLanguageUsage     ✓               ✗
hasStatus            ✓               ✗
isElement            ✓               ✗
hasHoldingInst.      ✓               ✗
```

These properties vary from reel to reel in real collections. A print may have
three nitrate reels and one later acetate replacement; each reel has its own
length; one reel may be tinted. Repairing `Carrier` would mean copying nearly
the whole property set of `Item` onto it, leaving two classes with the same
description.

### 2.2 `Carrier` encodes a role, not a kind of thing

A reel is the same kind of object whether it is the whole copy or one of five.
With a separate class, what the reel *is* depends on whether it has siblings.

```text
With Carrier: identity depends on position

  a single reel, held alone           the same reel, once reel 2 is found

  Item      <item/123>                Item      <item/123>
   └─ Carrier <carrier/456>            ├─ Carrier <carrier/456>
      (or collapse the two?)           └─ Carrier <carrier/789>


With Item composition: identity is stable

  Item <item/456>                     Item <item/900>  (group, new)
                                       ├─ hasComponent ─► Item <item/456>   unchanged
                                       └─ hasComponent ─► Item <item/789>
```

In practice reels move between copies, sets are completed from different
sources, and loose reels are held on their own. A relation can be added or
removed without touching the description of the object. A class cannot.

### 2.3 `Carrier` forces a wrapper onto every single-unit holding

Most holdings are a single unit: one reel, one cassette, one disc, one file. A
mandatory two-level structure requires two records for each of them, one of
which carries no information of its own.

```text
Mandatory two levels                  Optional composition

Manifestation                         Manifestation
 └─ Item      (empty wrapper)          └─ Item   identifier · format
     └─ Carrier  identifier · format             base · stock · extent
```

In one archive's catalogue the wrapper level is estimated to account for
70–80% of the records at these two levels. That is a local estimate, not a
measurement.

### 2.4 Contributed data rarely reaches the `Carrier` level

FIAFcore is populated by data donations from archives. Contributors typically
share their item-level data and nothing below it, even when their own
catalogues record reels, cassettes, or files as separate units.

This is separate from the question of internal management data. Barcodes,
locations, condition, and movements are typically not shared at any level,
whether the source records them on the item or on the unit. What is lost with
the unit level is description FIAFcore does want: per-reel base, stock, extent,
and colour.

```text
What the archive holds                   What it contributes

Manifestation                            Manifestation
 └─ Item                                  └─ Item
     ├─ unit   base · stock · extent
     ├─ unit   base · stock · extent         (nothing below)
     └─ unit   base · stock · extent
```

With a separate class, this makes `Carrier` a dead end: a level the ontology
defines but the data almost never fills, and one that cannot carry the
description even where it is filled (§2.1). It also makes the two kinds of
contribution structurally different, so a query written for one does not fit
the other.

With composition, an item-only contribution is a complete description, not a
truncated one. The Item is described where the contributor describes it, and
the number of units is stated as extent. If the contributor later shares
unit-level data, component Items are added beneath an Item that does not
change.

```text
Item-only contribution                   The same holding, units shared later

Item  "35mm print"                       Item  "35mm print"            unchanged
  extent: 5 reels                          extent: 5 reels
                                           ├─ hasComponent ─► Item "reel 1"
                                           ├─ hasComponent ─► Item "reel 2"
                                           └─ …
```

### 2.5 An ontology does not have to name the levels an interface shows

FIAFcore is an ontology and data model, not a cataloguing interface. A system
built on it is free to call component Items whatever suits its users and its
software, "carrier" included. Removing the `Carrier` class does not remove the
word from anyone's catalogue.

The National Library of Norway's catalogue is an example. For practical reasons
in the cataloguing system it uses two entities, `ITEM` and `ITEM_PART`. In the
current mapping `ITEM_PART` maps to `fiaf:Carrier`. If the data were remapped
to the proposed model, both entities would map to `fiaf:Item`, and the link
between them to `hasComponent`.

```text
In the cataloguing system               In FIAFcore, if remapped
(names chosen by the implementation)    (one class, one relation)

ITEM            "35mm print"     ──►    Item
 ├─ ITEM_PART   "reel 1"         ──►     ├─ hasComponent ─► Item
 └─ ITEM_PART   "reel 2"         ──►     └─ hasComponent ─► Item

another system: Item / Carrier   ──►    Item ─ hasComponent ─► Item
another system: items only       ──►    Item
```

The ontology therefore needs only what is common to all of these: a thing that
is held, and the fact that some held things are made up of others. The local
names for the levels stay local.

### 2.6 The source standards have item components, not a carrier entity

The texts below were checked on 2026-11-12. EN 15907 has not been checked.

| Source | Separate carrier entity? | Components of an item? |
| :--- | :--- | :--- |
| FIAF Manual (2016) | No. "Carrier type" is an attribute of Manifestation and Item | Yes, in the definition of Item |
| FRBR (1998, amended 2008) | No | Yes, with an item-to-item whole/part relationship |
| IFLA LRM (2017) | No | Yes in the definition of Item; no relationship defined |
| RDA | No | Yes, item-to-item relationships |

**FIAF Moving Image Cataloguing Manual**, 3.0 Definition (p. 67):

> An Item may consist of one or more components, i.e. the whole Item may consist
> of 1 reel or 5 reels, 2 VHS tapes or 1 DVD. An Item record may contain fields
> or scope for separate barcodes and condition information for each component
> of the item (each reel for example) if required.

The manual has no Carrier entity. Its "carrier type" (3.1.5.1) is an attribute:
"the medium on or the encoding format in which the Item is fixed", and for
digital files the specific carrier type is "the physical carrier storing the
digital file". The word "component" in the proposed property name follows the
manual's wording.

**FRBR**, 3.2.4: an item is "a single exemplar of a manifestation" and may
comprise "more than one physical object (e.g., a monograph issued as two
separately bound volumes, a recording issued on three separate compact
discs)". Section 5.3.6.1 defines a whole/part relationship between items,
"physical component of copy", and describes a discrete component as "a
separable physical piece constituting part of the whole item".

**IFLA LRM**, LRM-E5: "An item is in many instances a single physical object,
but in other cases, an item may consist of multiple physical pieces or
objects." LRM defines a whole–part relationship for manifestations (LRM-R26)
but none for items, so it supports the idea without supplying the relation.

**RDA** defines the relation that LRM leaves out. `rdai:P40034` "is container
of item" is "An item that is a discrete component of a larger item", and
`rdai:P40009` "is contained in item" is its counterpart. Both are published
elements with domain Item. `hasComponent` corresponds to `rdai:P40034`.

Sources:
[FIAF Manual](https://www.fiafnet.org/images/tinyUpload/E-Resources/Commission-And-PIP-Resources/CDC-resources/20160920_Fiaf_Manual-WEB.pdf),
[FRBR](https://www.ifla.org/files/assets/cataloguing/frbr/frbr_2008.pdf),
[IFLA LRM](https://www.ifla.org/files/assets/cataloguing/frbr-lrm/ifla-lrm-august-2017_rev201712.pdf),
[RDA Registry, item elements](https://www.rdaregistry.info/Elements/i/).

## 3. The proposed model

An Item is a single unit or a group of units. A group is needed only when there
are several units to describe, and is never required for a single unit.

```text
Work
 └─ hasManifestation ─► Manifestation
                          │
                          │  (A) single unit
                          ├─ hasItem ─► Item  "16mm print, 1 reel"
                          │              identifier · format · base · stock · extent
                          │
                          │  (B) group of units
                          └─ hasItem ─► Item  "35mm print, 5 reels"
                                         │   element · status · total extent
                                         ├─ hasComponent ─► Item "reel 1"
                                         ├─ hasComponent ─► Item "reel 2"     each with its own
                                         ├─ hasComponent ─► Item "reel 3"     identifier · base
                                         ├─ hasComponent ─► Item "reel 4"     stock · extent
                                         └─ hasComponent ─► Item "reel 5"

  (C) held, content not yet identified: an Item with no Manifestation
      Item  "unidentified 35mm reel"

  (C') the same, as a group
      Item  "unidentified print, 3 reels"
       ├─ hasComponent ─► Item "reel 1"
       ├─ hasComponent ─► Item "reel 2"
       └─ hasComponent ─► Item "reel 3"
```

Three conventions would go with the property:

1. **Describe at the level where a statement is true.** Nothing is inherited
   between a group and its components. The group says what holds for the whole
   copy; each component says what holds for that unit.
2. **A single unit may be one Item or a group with one component.** Both are
   valid. Which one is published follows how the source catalogues the
   holding; the mapping does not have to merge or split records. The counts in
   §5 come out the same either way.
3. **An Item needs no Manifestation.** Material that is held but not identified
   is still an Item. Identification later adds one `hasItem` link.

## 4. One model for three kinds of source

Sources differ in how many levels they record below the Manifestation. The
proposed model holds all three without changing shape, which is the main
practical gain.

```text
Source structure                         In FIAFcore
────────────────                         ───────────
1. Single level                          Item
   items only; units given as extent       extent: 5 reels

2. Two levels, always                    Item
   every item has parts, even one          └─ hasComponent ─► Item   (one or more)

3. Two levels, optional                  Item                        (single unit)
   parts only where there are several    Item
                                           ├─ hasComponent ─► Item   (several units)
                                           └─ hasComponent ─► Item
```

```text
Source record                            FIAFcore
─────────────                            ────────
item with no parts recorded       ──►    one Item, extent stated as "5 reels"
item with one part                ──►    one Item, or a group Item + one component,
                                         following the source
item with several parts           ──►    group Item + one component per part
part with no item                 ──►    one Item
```

The single-unit case is deliberately left to the source. If the catalogue
records one item with one part beneath it, that can be published as a group
Item with a single component, with each record keeping its own identity and
description. If the contributor prefers to merge the two, the result is one
Item, and the description of both records is carried onto it. FIAFcore does not
require either, which keeps mappings simple and lets each archive's data stay
close to how it is catalogued.

Data from all three can sit in one graph and be queried with one pattern. A
copy is found the same way in each (§5), and its description is read from the
Item and, where present, its components:

```sparql
# every base recorded for a copy, whichever level the source put it on
SELECT ?copy ?base WHERE {
  ?copy a fiaf:Item .
  FILTER NOT EXISTS { ?g fiaf:hasComponent ?copy }
  ?copy fiaf:hasComponent? ?x .
  ?x fiaf:hasBase ?base .
}
```

Two caveats apply across mixed sources:

* **Unit counts are only as good as the source.** A single-level source records
  no units, so counting Items without components reports one unit per copy.
  The number of reels is then available only where the source stated it as
  extent. A reliable reel count across
  all sources needs a rule such as "count components where present, otherwise
  use the reel extent, otherwise unknown". Copies can be counted reliably;
  units cannot.
* **The same fact sits at different levels.** One source states base on the
  copy, another on each reel. Queries must read both levels, as above, and a
  comparison between sources is a comparison of what each chose to record.

## 5. Counting

An objection to a single class is that copies and physical units can no longer
be counted separately. They can, provided `hasComponent` is used for
composition only. The cost is that the count becomes a query over structure
rather than over a class; see §7.

```text
copies  =  Items that are not a component of another Item
units   =  Items that have no components

                    copies   units
(A) single unit        1       1
(B) 5 reels            1       5
(B) group, 1 component 1       1
(C) orphan reel        1       1
(C') orphan, 3 reels   1       3
```

```sparql
# copies
SELECT (COUNT(?i) AS ?copies) WHERE {
  ?i a fiaf:Item .
  FILTER NOT EXISTS { ?g fiaf:hasComponent ?i }
}

# units
SELECT (COUNT(?i) AS ?units) WHERE {
  ?i a fiaf:Item .
  FILTER NOT EXISTS { ?i fiaf:hasComponent ?c }
}
```

Counting copies as "objects of `hasItem`" would miss every unidentified Item,
so the definition rests on composition instead.

## 6. What `hasComponent` is not for

The counting rules hold only while the relation keeps one meaning. Several
other relationships between held things look similar and must not reuse it.

```text
composition          group Item ── hasComponent ──► unit Item            proposed

housing / storage    reel ── (kept in) ──► can                           not in scope
                     file ── (stored on) ──► data tape                   not in scope
compilation          two films on one reel                               see §6.2
copying / source     duplicate ── (copy of) ──► original                 not defined
package dependency   DCP VF ── (supplements) ──► DCP OV                  not defined
```

### 6.1 Housing and storage

A film reel kept in a can and a file stored on a data tape are the same kind of
relationship: a held thing and the object that houses it. Some archives
catalogue their cans, boxes, and cassette cases as objects in their own right,
with barcodes and locations, just as they do data tapes and drives.

```text
Composition                      Housing                         Storage

print ──► reel 1                 reel 1 ──► can 0815             file A ──┐
      ──► reel 2                 reel 2 ──► can 0815             file B ──┼──► LTO tape 0042
      ──► reel 3                 reel 3 ──► can 0816             file C ──┘
                                 other film, reel 1 ──► can 0816 file D ──► tapes 0042, 0043

one whole, its own parts         container holds whatever is put in it, across works
a reel belongs to one copy       contents can be moved and the container reused
the print is its reels           the container is not the sum of its contents
```

Relating these with `hasComponent` would be wrong for three reasons:

* **The direction inverts.** In composition the group is the copy and the
  components are the units. In housing the container is the unit and the
  contents are the copies. One relation carrying both makes "no parent" and "no
  children" meaningless, and the counts in §5 fail.
* **A reel is not part of a can, and a file is not part of a tape.** Either can
  be moved to another container and remain the same object.
* **Housing crosses works.** One can or tape holds material from unrelated
  Works, and one large object spans several containers.

The source models agree that the container is not the item. LRM says of a file
on a disc that also contains other files: "the portion of the disc holding the
file is the physical carrier or item." The FIAF Manual records the storage
medium of a digital file as an attribute, the specific carrier type, not as a
record of its own.

**Proposed position:** cans, boxes, data tapes, and drives are not Items. Where
they are described as objects, they are storage entities of their own kind.
That is administrative collection management, alongside locations, barcodes,
condition, and movements: useful to the holding archive, rarely shared (§2.4),
and outside the scope of the core ontology. It could become a FIAFcore
extension later.

**A possible storage relation.** Keeping storage out of `hasComponent` does not
mean it can never be expressed. A separate relation would do it, and because it
is separate it could attach to any Item, a group or a component. That matters:
the reels of one print often sit in different cans, and the files of one
package on different tapes. The names below are placeholders, not proposed
terms.

```text
Item "35mm print"
 ├─ hasComponent ─► Item "reel 1" ── (is housed in) ──► can 0815
 └─ hasComponent ─► Item "reel 2" ── (is housed in) ──► can 0816

Item "DCP" ── (is housed in) ──► LTO tape 0042, LTO tape 0043
```

What sits at the far end is the open question:

* **A storage entity of its own class.** The counts in §5 are untouched, and
  the storage units in existing data get a class back. The class would need
  little more than an identifier and a type (`DataStorageFormat`, or a kind of
  can or box). Location, condition, and movements would remain administrative
  data outside the core.
* **An Item.** No new class, but a tape or can has no group and no components,
  so it would count as both a copy and a unit. The counting queries would need
  a further exclusion, which fails for a container that is empty.

The first option fits this proposal better. Whether the relation and a minimal
class belong in the core, with only the administrative detail left to an
extension, is not settled. Nothing is added on the branch.

Two consequences follow for the core ontology:

* The *type* of storage medium stays describable. An Item for a digital object
  can carry a `DataStorageFormat` through `hasFormat`, in line with the
  manual's specific carrier type. This says what the file is held on without
  describing the tape as an object. `FORMAT_TAXONOMY.md` prefers the medium and
  the stored object to be kept separate where possible, so this point needs to
  be reconciled with it.
* Deprecating `Carrier` removes the only class that mappings currently use for
  storage units. The Bundesarchiv mapping emits its storage units as Carriers.
  Until a storage relation or an extension exists, such data either stays on the deprecated class or
  is reduced to a format on the Item.

### 6.2 Compilations: several films on one unit

A print in several reels is one copy in many units. A compilation reel is the
reverse: one unit carrying several films. The FIAF Manual (E.2.1, p. 162)
distinguishes two cases, and they are modelled differently.

```text
Intended compilation                     Compilation for convenience
edited together for a showing            films that happen to share a reel,
or publication                           or were joined for storage

Work A ──┐                               Work A ─► Manifestation A ─► Item A ──┐
Work B ──┼─► aggregate Manifestation     Work B ─► Manifestation B ─► Item B ──┼─ same package
Work C ──┘        └─► Item (the reel)    Work C ─► Manifestation C ─► Item C ──┘  number
```

* **Intended compilation.** The manual treats this as a collection aggregate:
  one Manifestation embodying several Works, with its Item. If the compilation
  runs to several reels, that Item has components like any other.
* **Compilation for convenience.** The manual's example is "two short Charlie
  Chaplin films that happen to be acquired on one reel or transferred onto one
  tape for storage convenience". It is not an aggregate. Each film has "their
  own Work, Manifestation, and Item records, but those Items would have the
  same location/package number".

In-house compilation reels spliced together from many short reels fall under
the second case when the joining was for storage or handling, and under the
first when it was a curated programme. That is a cataloguing judgement the
manual already asks for.

Neither case needs `hasComponent`, and the second must not use it: the short
films are not components of a copy, and treating the reel as their group would
count one copy where there are several.

For the convenience case no new term is proposed. Each film's Item is described
separately, which keeps its own base, stock, extent, and history, and the
shared reel is expressed by the Items carrying the same identifier. The cost is
that unit counts report several units for one physical reel, unless Items with
a shared package identifier are counted once. If a stronger link proves
necessary, the candidate is a relation between peers, as in RDA's "is bound
with" (`rdai:P40032`), not a part relation.

This replaces an earlier idea in `CARRIER_AND_DIGITAL_MODELING.md` (§9.3 and
shape F in §10.3) of linking two Manifestations to a single shared Item, which
does not follow the manual.

### 6.3 Copying and package dependency

A duplicate and its source, and a DCP supplemental package and the package it
depends on, are relationships between separate copies. Neither is defined yet,
and neither is composition.

## 7. Drawbacks and risks

* **It is a breaking change.** `Carrier` and `hasCarrier` are published terms.
  Existing data and the BFI, Bundesarchiv, and National Library of Norway
  mappings use them and would need to be migrated. Deprecation softens this but
  means two patterns coexist for a time.
* **The class no longer tells you what an Item is.** Today `a fiaf:Carrier`
  says "this is a unit" and `a fiaf:Item` says "this is a copy". Under the
  proposal a copy, a group, a unit, and unidentified material are all `Item`,
  and the difference lives in the links between them. Every consumer has to
  know the conventions in §3.
* **Counting needs structural queries.** `COUNT(?x a fiaf:Item)` returns
  neither copies nor units. The queries in §5 are correct but less obvious, and
  `FILTER NOT EXISTS` can be slower on large graphs.
* **The counts depend on discipline the ontology cannot enforce.** OWL does not
  stop someone using `hasComponent` for storage or for packages. If that
  happens the counts go wrong without any error. Validation shapes could check
  this, but none exist.
* **Two valid shapes for a single unit.** A single unit may be one Item or a
  group with one component (§3). The counts agree, but any query that reads
  description has to look in both places.
* **No inheritance means wider queries.** "All nitrate holdings" must look at
  each Item and at its components. Nothing prevents a group and its components
  from carrying overlapping or contradictory statements.
* **Depth is unbounded.** Nothing prevents groups of groups. That may be useful
  for sets of sets, but consumers cannot assume two levels.
* **One unit carrying several films is not covered by the relation.** Housing,
  storage, and compilations for convenience (§6) are the cases where the
  physical unit is larger than the copy. The proposal handles them by scope and
  by shared identifiers, not by a term, and unit counts are weaker there.
* **It stretches the definition of Item.** The manual's Item is the product of
  a Manifestation. A component reel, an unidentified reel with no
  Manifestation, and possibly a storage medium all sit less comfortably under
  that wording than a complete identified copy does. A component is also
  reached from its Manifestation only through its group, not directly by
  `hasItem`.
* **It is unfamiliar.** Many archives and systems think in items and carriers.
  §2.5 answers this for interfaces, but people reading the data directly will
  need the mapping explained.
* **Storage units lose their class.** See §6.1.
* **EN 15907 has not been checked** (§2.6).

### Can validation mitigate these?

Partly. SHACL shapes cannot make the model simpler to read, but they can turn
several of the conventions into checks. FIAFcore receives its data through
mappings that the project runs, so validation can be a step in that pipeline
before data is published. No shapes exist in the repository yet.

| Risk | What SHACL could check |
| :--- | :--- |
| `hasComponent` used for storage | An Item whose format is a `DataStorageFormat` is neither a group nor a component |
| Structure drifting | Both ends of `hasComponent` are Items; a component has at most one group; no Item is its own component |
| Unbounded depth | A component has no components of its own, if two levels are made the rule |
| Unit counts from mixed sources | A group states its extent; an Item without components that states more than one reel is reported, so unit counts can fall back on extent |
| Contradiction between levels | A warning where a group and its components state different values for the same property |
| Two patterns during deprecation | A warning on any use of `Carrier` or `hasCarrier` |

What validation cannot do:

* It cannot tell a wrongly used relation from a correct one when the structure
  is valid. A supplemental DCP recorded as a component of the package it
  depends on passes every structural check.
* It does not make the class say what an Item is, or make the counting queries
  simpler. Published reference queries would address that better.
* It only covers data that is run through it.

The same shapes would be worth having regardless of this proposal. With a
separate `Carrier` class the checks are fewer, because the class does part of
the work, but the data problems in §2.1 and §2.4 remain.

## 8. Open points

* A property for component number or order. For now a reel number or reel title
  is carried in the component's label or identifier.
* Relations for copying and package dependency (§6.3).
* Whether a storage relation from an Item to a storage entity should be added,
  whether that entity is a class of its own or an Item, and whether it belongs
  in the core (§6.1).
* Whether an administrative extension for storage entities, containers,
  locations, and condition should exist, and where `DataStorageFormat` belongs
  if it does (§6.1).
* Whether Items sharing a unit need a relation between peers, or whether a
  shared identifier is enough (§6.2).
* Whether the depth of composition should be limited, and whether SHACL shapes
  should accompany the property (§7).
* A citation for `hasComponent`: the FIAF Manual's definition of Item (§2.6)
  could serve as its `dc:source`.
* EN 15907 remains to be checked.
* The BFI, Bundesarchiv, and National Library of Norway mappings still emit
  `Carrier` and `hasCarrier`. They remain valid against the deprecated terms and
  have not been migrated.
* Removing `Carrier` from the property domains and from the ontology would be a
  later, breaking step.
