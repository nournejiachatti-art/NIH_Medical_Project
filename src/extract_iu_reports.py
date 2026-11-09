
import xml.etree.ElementTree as ET
import pandas as pd

from pathlib import Path


# Project paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent

REPORTS_DIR = (
    PROJECT_ROOT
    / "data"
    / "iu_xray"
    / "raw"
    / "reports"
    / "ecgen-radiology"
)

OUTPUT_DIR = PROJECT_ROOT / "results"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def get_element_id(root, tag):
    """Return the ID attribute of the first matching element."""
    element = root.find(tag)

    if element is not None:
        return element.get("id", "")

    return ""


def extract_report(xml_path):
    """Extract clinical text and image IDs from one XML report."""

    root = ET.parse(xml_path).getroot()

    report_id = get_element_id(root, "uId")
    iu_id = get_element_id(root, "IUXRId")

    sections = {
        "comparison": "",
        "indication": "",
        "findings": "",
        "impression": ""
    }

    # Extract clinical text sections
    for element in root.iter("AbstractText"):
        label = element.get("Label", "").strip().lower()

        if label in sections:
            sections[label] = " ".join(
                "".join(element.itertext()).split()
            )

    # Extract associated image IDs
    image_ids = []

    for element in root.iter("parentImage"):
        image_id = element.get("id", "").strip()

        if image_id and image_id not in image_ids:
            image_ids.append(image_id)

    # Fallback: extract IDs from figure URLs
    if not image_ids:
        for element in root.iter("url"):
            url = (element.text or "").strip()

            if url:
                image_id = Path(url).stem

                if image_id not in image_ids:
                    image_ids.append(image_id)

    report = {
        "report_id": report_id,
        "iu_id": iu_id,
        **sections,
        "num_images": len(image_ids)
    }

    # One row per associated image
    pairs = []

    for image_id in image_ids:
        pairs.append({
            "report_id": report_id,
            "iu_id": iu_id,
            "image_id": image_id,
            "image_filename": image_id + ".png",
            "findings": sections["findings"],
            "impression": sections["impression"],
            "indication": sections["indication"]
        })

    return report, pairs


def main():

    xml_files = sorted(
        REPORTS_DIR.glob("*.xml"),
        key=lambda p: int(p.stem) if p.stem.isdigit() else p.stem
    )

    print(f"XML reports found: {len(xml_files)}")

    reports = []
    image_pairs = []
    errors = []

    for xml_path in xml_files:

        try:
            report, pairs = extract_report(xml_path)

            reports.append(report)
            image_pairs.extend(pairs)

        except Exception as error:
            errors.append({
                "file": xml_path.name,
                "error": str(error)
            })

    # Save report-level CSV
    reports_df = pd.DataFrame(reports)

    reports_df.to_csv(
        OUTPUT_DIR / "iu_reports.csv",
        index=False,
        encoding="utf-8-sig"
    )

    # Save image-report associations
    pairs_df = pd.DataFrame(image_pairs)

    pairs_df.to_csv(
        OUTPUT_DIR / "iu_image_report_pairs.csv",
        index=False,
        encoding="utf-8-sig"
    )

    # Save extraction errors if any
    if errors:
        pd.DataFrame(errors).to_csv(
            OUTPUT_DIR / "iu_extraction_errors.csv",
            index=False,
            encoding="utf-8-sig"
        )

    print("\nExtraction completed!")
    print(f"Reports extracted: {len(reports)}")
    print(f"Image-report associations: {len(image_pairs)}")
    print(f"Reports with images: {sum(r['num_images'] > 0 for r in reports)}")
    print(f"Reports without images: {sum(r['num_images'] == 0 for r in reports)}")
    print(f"Extraction errors: {len(errors)}")

    print(f"\nFiles saved in: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
