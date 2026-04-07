# LobeChat 接入教程

1. LobeChat → 设置 → 语言模型 → OpenAI
2. **API Key**: 粘贴 README 中的 Key
3. **API 代理地址**: `https://aiapiv2.pekpik.com/v1`
4. 保存后选择模型即可

Docker 部署：
```bash
docker run -d -e OPENAI_API_KEY=sk-xxx -e OPENAI_PROXY_URL=https://aiapiv2.pekpik.com/v1 -p 3210:3210 lobehub/lobe-chat
```
