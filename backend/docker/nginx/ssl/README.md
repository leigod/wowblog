# Nginx SSL 证书目录

生产环境启用 HTTPS 时，将证书放入此目录：

- `fullchain.pem` —— 证书链（含中间证书）
- `privkey.pem` —— 私钥

随后编辑 `../nginx.conf`，取消文件末尾 **443 server 段**的注释，并把 `server_name` 改为实际域名。

## 安全提醒

- **切勿**将真实证书提交到版本控制系统。
- 建议在仓库根 `.gitignore` 中忽略 `docker/nginx/ssl/*.pem`。
- 此目录随 docker-compose 以只读方式挂载到容器 `/etc/nginx/ssl`。
