import time
from typing import List, Dict, Optional


class ProductParser:
    """Класс для парсинга отдельного продукта из API ответа."""

    def __init__(self, product_data: Dict):
        self.product = product_data

    def parse_title(self) -> str:
        title = self.product.get("name", "")
        extra_parts = []

        # ищем объём
        for f in self.product.get("filter_labels", []):
            if f.get("filter") == "obem":
                vol = f.get("title", "")
                if vol:
                    # заменяем точку на запятую и убираем пробелы
                    vol = vol.replace(".", ",").replace(" ", "")
                    if vol not in title:
                        extra_parts.append(vol)

            elif f.get("filter") == "cvet":
                color = f.get("title", "")
                if color and color not in title:
                    extra_parts.append(color)

        if extra_parts:
            title += ", " + ", ".join(extra_parts)

        return title


    def parse_brand(self) -> Optional[str]:
        for block in self.product.get("description_blocks", []):
            if block["code"] == "brend" and block.get("values"):
                return block["values"][0]["name"]
        return None

    def parse_section(self) -> List[str]:
        section = []
        category = self.product.get("category", {})
        parent = category.get("parent")
        if parent:
            section.append(parent["name"])
        if category.get("name"):
            section.append(category["name"])
        return section

    def parse_price(self) -> Dict:
        original = self.product.get("prev_price") or self.product.get("price")
        current = self.product.get("price")
        sale_tag = ""
        if original and current and original > current:
            discount = round(100 - (current / original * 100))
            sale_tag = f"Скидка {discount}%"
        return {
            "current": float(current) if current else None,
            "original": float(original) if original else None,
            "sale_tag": sale_tag,
        }

    def parse_stock(self) -> Dict:
        return {
            "in_stock": bool(self.product.get("available")),
            "count": int(self.product.get("quantity_total") or 0),
        }

    def parse_assets(self) -> Dict:
        main_image = self.product.get("image_url")
        set_images = [main_image] if main_image else []
        return {
            "main_image": main_image,
            "set_images": set_images,
            "view360": [],
            "video": [],
        }

    def parse_metadata(self) -> Dict:
        metadata = {"__description": ""}
        for block in self.product.get("description_blocks", []):
            if block.get("values"):
                values = ", ".join([str(v["name"]) for v in block.get("values", []) if "name" in v])
                metadata[block["title"]] = values
            elif block.get("min") and block.get("max"):
                metadata[block["title"]] = f"{block['min']}–{block['max']}{block.get('unit', '')}"
        return metadata

    def parse_marketing_tags(self) -> List[str]:
        tags = set()
        if self.product.get("new"):
            tags.add("Новинка")
        if self.product.get("gift_package"):
            tags.add("Подарок")
        tags.update(fl["title"] for fl in self.product.get("filter_labels", []) if fl.get("title"))
        return list(tags)

    def parse_variants(self) -> int:
        variants = 0
        for block in self.product.get("description_blocks", []):
            if block["code"] in ["cvet", "obem"]:
                if block.get("values"):
                    variants += len(block["values"])
                elif block.get("min") and block.get("max"):
                    variants += 1
        return variants

    def to_dict(self, slug: str) -> Dict:
        timestamp = int(time.time())
        rpc = self.product.get("vendor_code") or self.product.get("uuid")
        url = f"https://alkoteka.com/product/{self.product.get('category', {}).get('slug')}/{slug}"

        return {
            "timestamp": timestamp,
            "RPC": str(rpc),
            "url": url,
            "title": self.parse_title(),
            "marketing_tags": self.parse_marketing_tags(),
            "brand": self.parse_brand(),
            "section": self.parse_section(),
            "price_data": self.parse_price(),
            "stock": self.parse_stock(),
            "assets": self.parse_assets(),
            "metadata": self.parse_metadata(),
            "variants": self.parse_variants(),
        }
