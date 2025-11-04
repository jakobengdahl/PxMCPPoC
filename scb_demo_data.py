#!/usr/bin/env python3
"""
Demo data for SCB MCP Server
Used when the actual SCB API is not accessible (e.g., in restricted environments)
"""

# Example metadata tree structure (root level)
DEMO_ROOT_METADATA = [
    {
        "id": "BE",
        "text": "Befolkning",
        "type": "l"  # folder
    },
    {
        "id": "AM",
        "text": "Arbetsmarknad",
        "type": "l"
    },
    {
        "id": "NV",
        "text": "Näringsverksamhet",
        "type": "l"
    },
    {
        "id": "HA",
        "text": "Hushållens ekonomi",
        "type": "l"
    },
    {
        "id": "OE",
        "text": "Offentlig ekonomi",
        "type": "l"
    }
]

DEMO_ROOT_METADATA_EN = [
    {
        "id": "BE",
        "text": "Population",
        "type": "l"
    },
    {
        "id": "AM",
        "text": "Labour market",
        "type": "l"
    },
    {
        "id": "NV",
        "text": "Business activities",
        "type": "l"
    },
    {
        "id": "HA",
        "text": "Household finances",
        "type": "l"
    },
    {
        "id": "OE",
        "text": "Public finances",
        "type": "l"
    }
]

# Example subcategories for Befolkning (BE)
DEMO_BE_SUBCATEGORIES = [
    {
        "id": "BE0101",
        "text": "Befolkningsstatistik",
        "type": "l"
    },
    {
        "id": "BE0102",
        "text": "Befolkningsprognos",
        "type": "l"
    }
]

DEMO_BE_SUBCATEGORIES_EN = [
    {
        "id": "BE0101",
        "text": "Population statistics",
        "type": "l"
    },
    {
        "id": "BE0102",
        "text": "Population forecast",
        "type": "l"
    }
]

# Example table metadata
DEMO_TABLE_METADATA = {
    "BE0101N1": {
        "sv": {
            "title": "Befolkning efter ålder och kön",
            "variables": {
                "Region": {
                    "code": "Region",
                    "text": "Region",
                    "values": ["00", "01", "03", "04"],
                    "valueTexts": ["Riket", "Stockholm", "Uppsala", "Södermanland"]
                },
                "Alder": {
                    "code": "Alder",
                    "text": "Ålder",
                    "values": ["0", "1-4", "5-9", "10-14"],
                    "valueTexts": ["0 år", "1-4 år", "5-9 år", "10-14 år"]
                },
                "Kon": {
                    "code": "Kon",
                    "text": "Kön",
                    "values": ["1", "2"],
                    "valueTexts": ["Män", "Kvinnor"]
                },
                "Tid": {
                    "code": "Tid",
                    "text": "År",
                    "values": ["2020", "2021", "2022", "2023"],
                    "valueTexts": ["2020", "2021", "2022", "2023"]
                }
            }
        },
        "en": {
            "title": "Population by age and sex",
            "variables": {
                "Region": {
                    "code": "Region",
                    "text": "Region",
                    "values": ["00", "01", "03", "04"],
                    "valueTexts": ["Whole country", "Stockholm", "Uppsala", "Södermanland"]
                },
                "Age": {
                    "code": "Age",
                    "text": "Age",
                    "values": ["0", "1-4", "5-9", "10-14"],
                    "valueTexts": ["0 years", "1-4 years", "5-9 years", "10-14 years"]
                },
                "Sex": {
                    "code": "Sex",
                    "text": "Sex",
                    "values": ["1", "2"],
                    "valueTexts": ["Men", "Women"]
                },
                "Time": {
                    "code": "Time",
                    "text": "Year",
                    "values": ["2020", "2021", "2022", "2023"],
                    "valueTexts": ["2020", "2021", "2022", "2023"]
                }
            }
        }
    }
}

# Example data response
DEMO_DATA_RESPONSE = {
    "BE0101N1": {
        "columns": [
            {"code": "Region", "text": "Region", "type": "d"},
            {"code": "Tid", "text": "År", "type": "t"},
            {"code": "value", "text": "Befolkning", "type": "c"}
        ],
        "data": [
            {"key": ["00", "2023"], "values": ["10521556"]},
            {"key": ["01", "2023"], "values": ["2415139"]},
            {"key": ["03", "2023"], "values": ["404074"]},
            {"key": ["04", "2023"], "values": ["301002"]}
        ],
        "metadata": {
            "title": "Befolkning efter region och år",
            "source": "SCB - Demo Data"
        }
    }
}


def get_demo_root_metadata(language="sv"):
    """Get demo root metadata"""
    return DEMO_ROOT_METADATA if language == "sv" else DEMO_ROOT_METADATA_EN


def get_demo_subcategories(path, language="sv"):
    """Get demo subcategories for a path"""
    if path == "BE":
        return DEMO_BE_SUBCATEGORIES if language == "sv" else DEMO_BE_SUBCATEGORIES_EN
    return []


def get_demo_table_metadata(table_id, language="sv"):
    """Get demo table metadata"""
    if table_id in DEMO_TABLE_METADATA:
        return DEMO_TABLE_METADATA[table_id].get(language, {})
    return {}


def get_demo_data(table_id):
    """Get demo data for a table"""
    return DEMO_DATA_RESPONSE.get(table_id, {})
