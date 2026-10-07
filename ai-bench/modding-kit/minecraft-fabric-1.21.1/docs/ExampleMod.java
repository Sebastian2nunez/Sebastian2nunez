// Versión: Minecraft 1.21.1 · Nombres de clase: MOJANG
// Fuente: fabric-docs/reference/1.21.1 (recortado: sin la parte de partículas)
package com.example.docs;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import net.fabricmc.api.ModInitializer;

public class ExampleMod implements ModInitializer {
	// Es buena práctica usar el id del mod como nombre del logger.
	public static final String MOD_ID = "example-mod";
	public static final Logger LOGGER = LoggerFactory.getLogger(MOD_ID);

	@Override
	public void onInitialize() {
		// Se ejecuta cuando Minecraft está listo para cargar mods.
		LOGGER.info("Hello Fabric world!");
	}
}
