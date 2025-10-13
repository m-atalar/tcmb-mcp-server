#!/usr/bin/env python3
"""TCMB MCP Server - Türkiye Cumhuriyet Merkez Bankası Döviz Kurları"""

import asyncio
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Any

import httpx
from mcp.server import Server
from mcp.types import Resource, Tool, TextContent, ImageContent, EmbeddedResource

# TCMB API endpoint'leri
TCMB_TODAY_URL = "https://www.tcmb.gov.tr/kurlar/today.xml"
TCMB_HISTORICAL_URL = "https://www.tcmb.gov.tr/kurlar/{year}{month}/{day}{month}{year}.xml"

app = Server("tcmb-mcp-server")


def parse_exchange_rates(xml_content: str) -> dict[str, Any]:
    """XML formatındaki döviz kurlarını parse et"""
    root = ET.fromstring(xml_content)

    # Tarih bilgisini al
    tarih = root.get("Tarih")
    bulletin_no = root.get("Bulten_No")

    rates = {
        "tarih": tarih,
        "bulten_no": bulletin_no,
        "kurlar": []
    }

    # Her bir para birimi için bilgileri topla
    for currency in root.findall("Currency"):
        code = currency.get("CurrencyCode")

        currency_data = {
            "kod": code,
            "isim": currency.findtext("Isim", ""),
            "birim": currency.findtext("Unit", "1"),
        }

        # ForexBuying ve ForexSelling (döviz alış-satış)
        forex_buying = currency.findtext("ForexBuying")
        forex_selling = currency.findtext("ForexSelling")

        # BanknoteBuying ve BanknoteSelling (efektif alış-satış)
        banknote_buying = currency.findtext("BanknoteBuying")
        banknote_selling = currency.findtext("BanknoteSelling")

        if forex_buying:
            currency_data["doviz_alis"] = forex_buying
        if forex_selling:
            currency_data["doviz_satis"] = forex_selling
        if banknote_buying:
            currency_data["efektif_alis"] = banknote_buying
        if banknote_selling:
            currency_data["efektif_satis"] = banknote_selling

        rates["kurlar"].append(currency_data)

    return rates


def format_rates_as_text(rates: dict[str, Any], currency_code: str = None) -> str:
    """Döviz kurlarını okunabilir metin olarak formatla"""
    text = f"📊 TCMB Döviz Kurları\n"
    text += f"📅 Tarih: {rates['tarih']}\n"
    text += f"📋 Bülten No: {rates['bulten_no']}\n\n"

    # Eğer belirli bir para birimi isteniyorsa sadece onu göster
    currencies = rates['kurlar']
    if currency_code:
        currencies = [c for c in currencies if c['kod'] == currency_code.upper()]
        if not currencies:
            return f"❌ {currency_code} para birimi bulunamadı."

    for currency in currencies:
        text += f"💱 {currency['kod']} - {currency['isim']}\n"
        text += f"   Birim: {currency['birim']}\n"

        if 'doviz_alis' in currency:
            text += f"   Döviz Alış: {currency['doviz_alis']} TL\n"
        if 'doviz_satis' in currency:
            text += f"   Döviz Satış: {currency['doviz_satis']} TL\n"
        if 'efektif_alis' in currency:
            text += f"   Efektif Alış: {currency['efektif_alis']} TL\n"
        if 'efektif_satis' in currency:
            text += f"   Efektif Satış: {currency['efektif_satis']} TL\n"
        text += "\n"

    return text


@app.list_resources()
async def list_resources() -> list[Resource]:
    """Mevcut kaynakları listele"""
    return [
        Resource(
            uri="tcmb://exchange-rates/today",
            name="Güncel Döviz Kurları",
            mimeType="text/plain",
            description="TCMB'nin güncel döviz kurları"
        )
    ]


@app.read_resource()
async def read_resource(uri: str) -> str:
    """Kaynak içeriğini oku"""
    if uri == "tcmb://exchange-rates/today":
        async with httpx.AsyncClient() as client:
            response = await client.get(TCMB_TODAY_URL)
            response.raise_for_status()
            rates = parse_exchange_rates(response.text)
            return format_rates_as_text(rates)
    else:
        raise ValueError(f"Bilinmeyen kaynak: {uri}")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """Mevcut araçları listele"""
    return [
        Tool(
            name="get_exchange_rates",
            description="TCMB'den güncel veya geçmiş döviz kurlarını getirir. Belirli bir para birimi veya tüm kurları sorgulayabilirsiniz.",
            inputSchema={
                "type": "object",
                "properties": {
                    "date": {
                        "type": "string",
                        "description": "İsteğe bağlı. Geçmiş bir tarih için kurları getirir (format: YYYY-MM-DD). Belirtilmezse güncel kurlar getirilir.",
                    },
                    "currency_code": {
                        "type": "string",
                        "description": "İsteğe bağlı. Belirli bir para birimi kodu (örn: USD, EUR, GBP). Belirtilmezse tüm kurlar getirilir.",
                    },
                },
            },
        ),
        Tool(
            name="list_currencies",
            description="TCMB'de mevcut tüm para birimlerinin kodlarını ve isimlerini listeler.",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Araç çağrısını işle"""

    if name == "get_exchange_rates":
        date_str = arguments.get("date")
        currency_code = arguments.get("currency_code")

        async with httpx.AsyncClient() as client:
            if date_str:
                # Geçmiş tarih için URL oluştur
                try:
                    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                    url = TCMB_HISTORICAL_URL.format(
                        year=date_obj.strftime("%Y"),
                        month=date_obj.strftime("%m"),
                        day=date_obj.strftime("%d")
                    )
                except ValueError:
                    return [TextContent(
                        type="text",
                        text="❌ Hatalı tarih formatı. Lütfen YYYY-MM-DD formatında girin (örn: 2024-01-15)"
                    )]
            else:
                # Güncel kurlar
                url = TCMB_TODAY_URL

            try:
                response = await client.get(url)
                response.raise_for_status()
                rates = parse_exchange_rates(response.text)
                text = format_rates_as_text(rates, currency_code)

                return [TextContent(type="text", text=text)]
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 404:
                    return [TextContent(
                        type="text",
                        text=f"❌ Belirtilen tarih için kur bilgisi bulunamadı. TCMB sadece iş günleri için kur yayınlar."
                    )]
                return [TextContent(
                    type="text",
                    text=f"❌ TCMB API hatası: {str(e)}"
                )]
            except Exception as e:
                return [TextContent(
                    type="text",
                    text=f"❌ Hata oluştu: {str(e)}"
                )]

    elif name == "list_currencies":
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(TCMB_TODAY_URL)
                response.raise_for_status()
                rates = parse_exchange_rates(response.text)

                text = "💱 TCMB'de Mevcut Para Birimleri:\n\n"
                for currency in rates['kurlar']:
                    text += f"• {currency['kod']:6s} - {currency['isim']}\n"

                return [TextContent(type="text", text=text)]
            except Exception as e:
                return [TextContent(
                    type="text",
                    text=f"❌ Hata oluştu: {str(e)}"
                )]

    else:
        raise ValueError(f"Bilinmeyen araç: {name}")


async def main():
    """Ana fonksiyon - MCP server'ı başlat"""
    from mcp.server.stdio import stdio_server

    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
