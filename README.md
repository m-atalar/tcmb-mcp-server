# TCMB MCP Server

Türkiye Cumhuriyet Merkez Bankası (TCMB) döviz kurları için MCP (Model Context Protocol) sunucusu.

## Özellikler

- Güncel döviz kurlarını sorgulama
- Geçmiş tarih kurlarını sorgulama
- Belirli para birimleri için kur bilgisi

## Kurulum

```bash
pip install -e .
```

## Kullanım

```bash
tcmb-mcp-server
```

## MCP Inspector ile Test

```bash
npx @modelcontextprotocol/inspector tcmb-mcp-server
```
