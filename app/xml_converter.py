"""
xml_converter.py — Convert MedQuAD XML files to readable TXT for the RAG pipeline.

Reads every .xml file from ./data/, extracts Question/Answer pairs,
and writes structured .txt files into ./txt_data/.
"""

import xml.etree.ElementTree as ET
from pathlib import Path

from app.config import DATA_DIR, TXT_DATA_DIR
from app.utils import setup_logger

logger = setup_logger("xml_converter")


def parse_xml_file(xml_path: Path) -> list[dict]:
    """
    Parse a single MedQuAD XML file and return a list of QA entries.

    Each entry contains: topic, question, answer, source_file.
    """
    entries = []
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()

        # Extract topic
        focus_el = root.find("Focus")
        topic = focus_el.text.strip() if focus_el is not None and focus_el.text else "Unknown"

        # Extract QA pairs
        for qa_pair in root.findall(".//QAPair"):
            q_el = qa_pair.find("Question")
            a_el = qa_pair.find("Answer")

            question = q_el.text.strip() if q_el is not None and q_el.text else ""
            answer = a_el.text.strip() if a_el is not None and a_el.text else ""

            if question and answer:
                entries.append({
                    "topic": topic,
                    "question": question,
                    "answer": answer,
                    "source_file": xml_path.name,
                })

    except ET.ParseError as exc:
        logger.warning("Malformed XML skipped: %s — %s", xml_path.name, exc)
    except Exception as exc:
        logger.error("Error parsing %s — %s", xml_path.name, exc)

    return entries


def convert_all_xml_to_txt() -> int:
    """
    Convert every XML file in DATA_DIR to a structured TXT file in TXT_DATA_DIR.

    Returns
    -------
    int
        Number of TXT files created.
    """
    xml_files = sorted(DATA_DIR.rglob("*.xml"))
    if not xml_files:
        logger.warning("No XML files found in %s", DATA_DIR)
        return 0

    logger.info("Found %d XML files in %s", len(xml_files), DATA_DIR)
    TXT_DATA_DIR.mkdir(parents=True, exist_ok=True)

    files_created = 0

    for xml_path in xml_files:
        entries = parse_xml_file(xml_path)
        if not entries:
            continue

        # Build readable text content
        lines = []
        for entry in entries:
            lines.append(f"Topic: {entry['topic']}")
            lines.append(f"Question: {entry['question']}")
            lines.append(f"Answer: {entry['answer']}")
            lines.append(f"Source: {entry['source_file']}")
            lines.append("")  # blank separator

        # folder_name = xml_path.parent.name
        # txt_name = f"{folder_name}_{xml_path.stem}.txt"
        # txt_path = TXT_DATA_DIR / txt_name
        # txt_path.write_text("\n".join(lines), encoding="utf-8")

        # Preserve folder structure inside txt_data
        relative_folder = xml_path.parent.relative_to(DATA_DIR)

        # Create same folder inside txt_data
        output_folder = TXT_DATA_DIR / relative_folder
        output_folder.mkdir(parents=True, exist_ok=True)

        # Keep same filename, only change extension
        txt_name = xml_path.stem + ".txt"

        # Final output path
        txt_path = output_folder / txt_name

        # Write TXT file
        txt_path.write_text("\n".join(lines), encoding="utf-8")

        files_created += 1

    logger.info("Created %d TXT files in %s", files_created, TXT_DATA_DIR)
    return files_created


# ── CLI entry point ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    count = convert_all_xml_to_txt()
    print(f"Conversion complete — {count} files created.")
