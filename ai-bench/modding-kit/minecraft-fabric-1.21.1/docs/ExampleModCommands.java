// Versión: Minecraft 1.21.1 · Nombres de clase: MOJANG
// Fuente: fabric-docs/reference/1.21.1 (recortado: solo comando simple, con permiso y con argumento)
package com.example.docs.command;

import com.mojang.brigadier.arguments.IntegerArgumentType;
import com.mojang.brigadier.context.CommandContext;
import net.fabricmc.api.ModInitializer;
import net.fabricmc.fabric.api.command.v2.CommandRegistrationCallback;
import net.minecraft.commands.CommandSourceStack;
import net.minecraft.commands.Commands;
import net.minecraft.network.chat.Component;

public class ExampleModCommands implements ModInitializer {
	private static int executeRequiredCommand(CommandContext<CommandSourceStack> context) {
		context.getSource().sendSuccess(() -> Component.literal("Called /required_command."), false);
		return 1;
	}

	private static int executeCommandWithArg(CommandContext<CommandSourceStack> context) {
		int value = IntegerArgumentType.getInteger(context, "value");
		context.getSource().sendSuccess(() -> Component.literal("Called /command_with_arg with value = %s".formatted(value)), false);
		return 1;
	}

	@Override
	public void onInitialize() {
		// Comando simple: /test_command
		CommandRegistrationCallback.EVENT.register((dispatcher, registryAccess, environment) -> {
			dispatcher.register(Commands.literal("test_command").executes(context -> {
				context.getSource().sendSuccess(() -> Component.literal("Called /test_command."), false);
				return 1;
			}));
		});

		// Comando que exige permisos de operador: /required_command
		CommandRegistrationCallback.EVENT.register((dispatcher, registryAccess, environment) -> {
			dispatcher.register(Commands.literal("required_command")
					.requires(source -> source.hasPermission(1))
					.executes(ExampleModCommands::executeRequiredCommand));
		});

		// Comando con un argumento entero: /command_with_arg <value>
		CommandRegistrationCallback.EVENT.register((dispatcher, registryAccess, environment) -> {
			dispatcher.register(Commands.literal("command_with_arg")
					.then(Commands.argument("value", IntegerArgumentType.integer())
							.executes(ExampleModCommands::executeCommandWithArg)));
		});
	}
}
