# Kit de modding: Minecraft 1.21.1 + Fabric + Mojang mappings

Plantilla para trabajar con Cline y un modelo local.

## 1. Preparar el proyecto
1. Instala **JDK 21**.
2. Genera la plantilla en https://fabricmc.net/develop/template eligiendo **1.21.1** y mappings **Mojang** (si no los ofrece, usa los que ofrezca y avisa en `docs/`).
3. Comprueba que la plantilla compila: `./gradlew build` (la primera vez descarga mucho).
4. En `build.gradle` suele aparecer algo como `loom.officialMojangMappings()` si usas Mojang. Confírmalo.
5. Copia el `.clinerules` de esta carpeta a la raíz del proyecto.

## 2. Preparar `docs/` (poco material, para no gastar contexto)
Copia la carpeta `docs/` de este kit a la raíz de tu proyecto del mod. Contiene:
- `00-mappings.md`: tabla Yarn → Mojang con los nombres confirmados en el código de referencia.
- `ExampleMod.java` y `ExampleModCommands.java`: ejemplos oficiales de fabric-docs (`reference/1.21.1`, Mojang mappings), recortados a lo mínimo.

Son unos 1.500 tokens en total. Si necesitas más (objetos, bloques...), copia solo los archivos de `reference/1.21.1/src/main/java/com/example/docs/` que hagan falta y ponles la cabecera `Versión... · Nombres de clase: MOJANG`.

No copies la guía en Markdown de `versions/1.21.1/develop/...`: usa nombres de Yarn en el texto y no incluye el código (lo importa desde `reference`).

## 3. Primera prueba en Cline
Empieza en modo **Plan**, y luego pasa a **Act**:

> Quiero que el mod añada el comando `/rubi`. Al ejecutarlo, el jugador recibe 3 diamantes. Usa solo la API documentada en `docs/`. Compila con `./gradlew build` y corrige hasta que compile.

## 4. Cómo juzgarlo
- Compila: bien.
- Funciona con `./gradlew runClient` y escribiendo `/rubi`: perfecto.
- Apunta cuántas correcciones necesitó y de qué tipo (API inventada, nombres de Yarn mezclados, imports, versión equivocada).

## Ajustes recomendados del servidor
`llama-server ... --reasoning-budget 3000` y un contexto de 20K a 32K (más contexto baja la velocidad si no cabe en la VRAM).
