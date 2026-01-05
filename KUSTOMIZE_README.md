# 🚀 Kustomize - Estrutura Multi-Ambiente

## Estrutura do Projeto

```
K8s-Config/
├── Apps/                                ← BASE (aplicações)
│   ├── api.yml
│   ├── consumidor.yml
│   ├── produtor.yml
│   ├── ui.yml
│   ├── hpa.yml
│   └── kustomization.yaml              ← Lista os recursos (namespace: grupo2)
│
└── Infraestrutura/
    ├── Local/                           ← OVERLAY para Docker Desktop
    │   ├── kustomization.yaml           ← Herda Apps/ + Infraestrutura Local
    │   ├── Mongo/
    │   ├── RabbitMQ/
    │   ├── Monitoring/ (Prometheus + Grafana)
    │   └── Metrics/
    │
    └── Remote/                          ← OVERLAY para Cluster Remoto
        ├── kustomization.yaml           ← Herda Apps/ + Infraestrutura Remota
        ├── Mongo/
        ├── Secrets/
        └── Monitoring/ (PodMonitors)
```

---

## 🎯 Como Funciona

### BASE: Apps/
Contém **apenas as aplicações**:
- API, Consumidor, Produtor, UI
- HorizontalPodAutoscaler (HPA)

**Importante**: O nome da pasta `Apps/` **não foi alterado** para compatibilidade com GitHub Actions.

### OVERLAY: Infraestrutura/Local
Herda `Apps/` e adiciona:
- ✅ MongoDB completo (local)
- ✅ RabbitMQ completo (local)
- ✅ Prometheus + Grafana
- ✅ Metrics Server
- ✅ Namespace: grupo2

### OVERLAY: Infraestrutura/Remote
Herda `Apps/` e adiciona:
- ✅ MongoDB completo (remoto)
- ✅ RabbitMQ Secret (usa RabbitMQ compartido)
- ✅ PodMonitors (para Prometheus compartido)
- ✅ Namespace: grupo2

---

## 🚀 Como Usar

### Desplegar en Local (Docker Desktop)

```bash
# Desplegar tudo (Apps + Infraestrutura Local)
kubectl apply -k K8s-Config/Infraestrutura/Local

# Ver o que será desplegado (sem aplicar)
kubectl kustomize K8s-Config/Infraestrutura/Local

# Verificar
kubectl get all -n grupo2

# Eliminar tudo
kubectl delete -k K8s-Config/Infraestrutura/Local
```

### Desplegar en Remoto (Cluster Universidad)

```bash
# Manual
kubectl apply -k K8s-Config/Infraestrutura/Remote

# Automático via ArgoCD
# Usa: argo-application_remote.yml
# Path: K8s-Config/Infraestrutura/Remote
```

---

## 📋 Ficheros ArgoCD

### argo-application_local.yml
```yaml
path: K8s-Config/Infraestrutura/Local
```
**Uso**: Para desplegar en tu Docker Desktop via ArgoCD local

### argo-application_remote.yml
```yaml
path: K8s-Config/Infraestrutura/Remote
```
**Uso**: Para desplegar en el cluster remoto (universidad) via ArgoCD

---

## 🔄 Workflow de Cambios

### Cambiar algo en las APPS (afecta a todos):

```bash
# 1. Editar en Apps/
nano K8s-Config/Apps/api.yml

# 2. Commit
git add K8s-Config/Apps/
git commit -m "Update API image"
git push origin main

# 3. Resultado
# ✅ Local: Se actualiza al hacer kubectl apply -k
# ✅ Remoto: ArgoCD sincroniza automáticamente
```

### Cambiar SOLO en Local:

```bash
# Editar en Infraestrutura/Local/
nano K8s-Config/Infraestrutura/Local/Mongo/mongo.yml

# Solo afecta al local
kubectl apply -k K8s-Config/Infraestrutura/Local
```

### Cambiar SOLO en Remoto:

```bash
# Editar en Infraestrutura/Remote/
nano K8s-Config/Infraestrutura/Remote/Mongo/mongo.yml

# Commit y push
git add K8s-Config/Infraestrutura/Remote/
git push origin main

# ArgoCD sincroniza automáticamente
```

---

## ✅ Ventajas de Esta Estructura

| Ventaja | Detalle |
|---------|---------|
| **Sin duplicación** | Apps/ se define una vez, ambos overlays la heredan |
| **GitHub Actions compatible** | Apps/ mantiene su nombre |
| **Separación clara** | Apps vs Infraestrutura |
| **Multi-ambiente** | Local (completo) vs Remote (compartido) |
| **GitOps** | ArgoCD sincroniza automáticamente |

---

## 🧪 Comandos de Verificación

```bash
# Ver los recursos que se van a crear en Local
kubectl kustomize K8s-Config/Infraestrutura/Local | grep "kind:"

# Ver los recursos que se van a crear en Remoto
kubectl kustomize K8s-Config/Infraestrutura/Remote | grep "kind:"

# Contar cuántos recursos en Local
kubectl kustomize K8s-Config/Infraestrutura/Local | grep "^kind:" | wc -l

# Contar cuántos recursos en Remoto
kubectl kustomize K8s-Config/Infraestrutura/Remote | grep "^kind:" | wc -l
```

---

## 📊 Comparación: Local vs Remoto

| Recurso | Local | Remoto |
|---------|-------|--------|
| **Apps** | ✅ (hereda de Apps/) | ✅ (hereda de Apps/) |
| **Mongo** | ✅ Completo | ✅ Completo |
| **RabbitMQ** | ✅ Completo (propio) | ❌ Solo Secret (compartido) |
| **Prometheus** | ✅ Completo (propio) | ❌ PodMonitors (compartido) |
| **Grafana** | ✅ | ❌ (compartido) |
| **Metrics Server** | ✅ | ❌ (ya existe) |

---

## ⚠️ Notas Importantes

1. **Apps/** no se cambió de nombre → GitHub Actions funcionan sin cambios
2. **Namespace grupo2** está en ambos overlays
3. **ArgoCD**: Usa `argo-application_remote.yml` para el cluster remoto
4. **ArgoCD**: Usa `argo-application_local.yml` para Docker Desktop (opcional)

---

## 🎓 Para o Relatório

Podes explicar assim:

> "O projeto implementa Kustomize para gestão multi-ambiente:
> 
> - **Base (Apps/)**: Aplicações reutilizáveis
> - **Overlay Local**: Infraestrutura completa para Docker Desktop
> - **Overlay Remote**: Infraestrutura adaptada ao cluster universitário
> 
> Esta arquitetura elimina duplicação de código e permite despliegues automatizados via ArgoCD (GitOps)."

---

## 🔗 Próximos Pasos

1. **Testar Local**:
   ```bash
   kubectl apply -k K8s-Config/Infraestrutura/Local
   ```

2. **Configurar ArgoCD Remoto**:
   ```bash
   kubectl apply -f argo-application_remote.yml
   ```

3. **Verificar**:
   ```bash
   kubectl get all -n grupo2
   ```

---

**Estado**: ✅ Kustomize configurado correctamente
**Estructura**: Apps/ (base) + Local/Remote (overlays)
**Compatible**: GitHub Actions mantém compatibilidade com Apps/
