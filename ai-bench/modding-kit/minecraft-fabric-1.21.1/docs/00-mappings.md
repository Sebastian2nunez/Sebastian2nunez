Versión: Minecraft 1.21.1 · Nombres de clase: MOJANG (oficiales)
Fuente: ejemplos compilables de fabric-docs, carpeta reference/1.21.1

# Mappings: la guía en prosa de Fabric usa nombres de Yarn, el código usa Mojang

Si lees documentación de Fabric que dice una cosa y el código de `docs/` dice otra, manda el CÓDIGO (Mojang).

| Yarn (texto de las guías) | Mojang (lo que debes escribir) |
|---|---|
| ServerCommandSource | CommandSourceStack |
| CommandManager (`literal`, `argument`) | Commands (`Commands.literal`, `Commands.argument`) |
| Text (`Text.literal`) | Component (`Component.literal`) |
| source.sendFeedback(...) | source.sendSuccess(() -> Component.literal("..."), false) |
| Identifier | ResourceLocation (`ResourceLocation.fromNamespaceAndPath(MOD_ID, "nombre")`) |
| nivel de permiso | `source.hasPermission(1)` |

Otros nombres confirmados en el código de referencia:
- Registrar un objeto: `Registry.register(BuiltInRegistries.ITEM, ResourceLocation.fromNamespaceAndPath(MOD_ID, id), item)`
- Propiedades de un objeto: `new Item.Properties()`
- Pestañas creativas: `ItemGroupEvents.modifyEntriesEvent(CreativeModeTabs.INGREDIENTS).register(itemGroup -> itemGroup.accept(item))`
- Comandos: se registran con `CommandRegistrationCallback.EVENT.register((dispatcher, registryAccess, environment) -> { ... })`

## Lo que estos documentos NO cubren
- Cómo obtener al jugador que ejecuta un comando y cómo darle objetos.
Si lo necesitas y no está en `docs/`, di claramente que no lo sabes y pregunta; no lo inventes. Si el compilador marca un nombre como inexistente, no lo adivines.
