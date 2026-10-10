#!/usr/bin/env python3
"""Replace misleading held articles with clearly labelled, conservative editorial drafts.

These are not medically fact-checked; keep noindex until individually reviewed.
"""
from pathlib import Path
from html import escape
import json
import re

root = Path(__file__).resolve().parents[1]
catalog = {m["file"]: m for m in json.loads((root / "docs/articles_meta.json").read_text(encoding="utf-8"))}
hold = json.loads((root / "audits/title-triage-2026-10-11.json").read_text(encoding="utf-8"))["flagged_articles"]
copy = {
 "en": ("Editorial review: ", "This topic is being reviewed by the Body Advice editorial team. The previous version included personal accounts that could not be independently verified and has been withdrawn.", "What to consider", "Discomfort can have different causes. Avoid forcing movements or applying strong pressure to painful areas. Adjust activities according to comfort and seek qualified advice for persistent or worsening symptoms.", "When to seek help", "Seek prompt medical advice for severe pain, new weakness, numbness, significant swelling, fever or symptoms following an injury. Emergency symptoms require urgent care.", "This page is an interim editorial notice, not a medical guide or product recommendation."),
 "de": ("Redaktionelle Prüfung: ", "Dieses Thema wird von der Body Advice Redaktion geprüft. Die frühere Fassung enthielt persönliche Berichte, die nicht unabhängig bestätigt werden konnten, und wurde zurückgezogen.", "Worauf Sie achten können", "Beschwerden können unterschiedliche Ursachen haben. Vermeiden Sie erzwungene Bewegungen und starken Druck auf schmerzende Stellen. Passen Sie Aktivitäten Ihrem Wohlbefinden an und holen Sie bei anhaltenden Beschwerden fachlichen Rat ein.", "Wann Hilfe nötig ist", "Bei starken Schmerzen, neuer Schwäche, Taubheit, deutlicher Schwellung, Fieber oder Beschwerden nach einer Verletzung ist eine zeitnahe medizinische Abklärung sinnvoll.", "Dies ist ein vorläufiger redaktioneller Hinweis, kein medizinischer Ratgeber oder eine Produktempfehlung."),
 "it": ("Revisione editoriale: ", "Questo argomento è in revisione presso Body Advice. La versione precedente conteneva testimonianze personali non verificabili in modo indipendente ed è stata ritirata.", "Cosa considerare", "Il fastidio può avere cause diverse. Evita movimenti forzati e pressioni intense sulle zone doloranti. Adatta le attività al tuo comfort e chiedi un parere professionale se i sintomi persistono o peggiorano.", "Quando chiedere aiuto", "Per dolore intenso, nuova debolezza, intorpidimento, gonfiore importante, febbre o sintomi dopo un trauma, consulta tempestivamente un professionista sanitario.", "Questa pagina è un avviso editoriale provvisorio, non una guida medica o una raccomandazione commerciale."),
 "es": ("Revisión editorial: ", "Body Advice está revisando este tema. La versión anterior incluía relatos personales que no se pudieron verificar de forma independiente y se ha retirado.", "Qué conviene tener en cuenta", "Las molestias pueden tener distintas causas. Evita forzar movimientos o ejercer presión intensa sobre zonas dolorosas. Adapta la actividad a tu comodidad y busca asesoramiento profesional si los síntomas persisten o empeoran.", "Cuándo consultar", "Ante dolor intenso, debilidad nueva, entumecimiento, hinchazón importante, fiebre o síntomas después de una lesión, busca atención sanitaria sin demora.", "Esta página es un aviso editorial provisional, no una guía médica ni una recomendación de productos."),
 "fr": ("Révision éditoriale : ", "Body Advice révise actuellement ce sujet. La version précédente contenait des récits personnels qui n'ont pas pu être vérifiés de manière indépendante et a été retirée.", "Points à considérer", "Les gênes peuvent avoir plusieurs causes. Évitez les mouvements forcés et les pressions fortes sur les zones douloureuses. Adaptez vos activités à votre confort et demandez conseil si les symptômes persistent ou s'aggravent.", "Quand demander de l'aide", "En cas de douleur intense, de faiblesse nouvelle, d'engourdissement, de gonflement important, de fièvre ou de symptômes après une blessure, consultez rapidement.", "Cette page est un avis éditorial provisoire, pas un guide médical ni une recommandation de produit."),
}
count = 0
for item in hold:
    rel = item["file"]
    if rel not in catalog:
        raise ValueError("Missing catalog item: " + rel)
    lang = item["lang"]
    topic = catalog[rel].get("topic", "Wellness")
    title = copy[lang][0] + topic
    c = copy[lang]
    path = root / "docs" / rel
    if not path.is_file():
        raise FileNotFoundError(path)
    html = f'''<!doctype html><html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,follow"><title>{escape(title)}</title><meta name="description" content="{escape(c[1], quote=True)}"><style>body{{font:18px/1.7 system-ui,sans-serif;background:#fafbf8;color:#243b30;margin:0}}main{{max-width:760px;margin:auto;padding:3rem 1.25rem}}h1{{font-size:clamp(2rem,5vw,3rem);line-height:1.2}}a{{color:#176b58}}</style></head><body><main><a href="/articles-{lang}.html">Body Advice</a><h1>{escape(title)}</h1><p>{escape(c[1])}</p><h2>{escape(c[2])}</h2><p>{escape(c[3])}</p><h2>{escape(c[4])}</h2><p>{escape(c[5])}</p><p><small>{escape(c[6])}</small></p></main></body></html>'''
    path.write_text(html + "\n", encoding="utf-8")
    count += 1
print(f"Replaced {count} misleading articles with transparent noindex editorial notices")
