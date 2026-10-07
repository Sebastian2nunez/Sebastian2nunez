# Kit de modding: Minecraft 1.21.1 + Fabric + Mojang mappings

Plantilla para trabajar con Cline y un modelo local.

## 1. Preparar el proyecto
1. Instala **JDK 21**.
2. Genera la plantilla en https://fabricmc.net/develop/template eligiendo **1.21.1** y mappings **Mojang** (si no los ofrece, usa los que ofrezca y avisa en `docs/`).
3. Comprueba que la plantilla compila: `./gradlew build` (la primera vez descarga mucho).
4. En `build.gradle` suele aparecer algo como `loom.officialMojangMappings()` si usas Mojang. Confírmalo.
5. Copia el `.clinerules` de esta carpeta a la raíz del proyecto.

## 2. Preparar `docs/` (poco material, para no gastar contexto)
Crea `docs/` en la raíz del proyecto y copia dentro:
- Las guías de **Getting Started** y de **Commands** de la documentación de Fabric para 1.21.1 (están en el repo `FabricMC/fabric-docs`; busca la versión correcta).
- Los ejemplos relacionados de la carpeta `reference` de ese repo, en `docs/reference/`.
- Al principio de cada archivo, una línea que diga qué nombres usa ("nombres de clase en Yarn" o "en Mojang").

Con 3 a 5 archivos pequeños basta.

## 3. Primera prueba en Cline
Empieza en modo **Plan**, y luego pasa a **Act**:

> Quiero que el mod añada el comando `/rubi`. Al ejecutarlo, el jugador recibe 3 diamantes. Usa solo la API documentada en `docs/`. Compila con `./gradlew build` y corrige hasta que compile.

## 4. Cómo juzgarlo
- Compila: bien.
- Funciona con `./gradlew runClient` y escribiendo `/rubi`: perfecto.
- Apunta cuántas correcciones necesitó y de qué tipo (API inventada, nombres de Yarn mezclados, imports, versión equivocada).

## Ajustes recomendados del servidor
`llama-server ... --reasoning-budget 3000` y un contexto de 20K a 32K (más contexto baja la velocidad si no cabe en la VRAM).
