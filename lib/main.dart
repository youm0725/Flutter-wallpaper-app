import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'core/router/app_router.dart';
import 'core/theme/app_theme.dart';
import 'providers/theme_provider.dart';

void main() {
  runApp(
    const ProviderScope(
      child: WallpaperApp(),
    ),
  );
}

/// Root widget of the application listening to persisted theme state.
class WallpaperApp extends ConsumerWidget {
  const WallpaperApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // Watch the async theme provider — fall back to ThemeMode.system while loading.
    final asyncThemeMode = ref.watch(themeModeProvider);
    final themeMode = asyncThemeMode.value ?? ThemeMode.system;

    return MaterialApp.router(
      title: 'Wallpaper Gallery',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.lightTheme,
      darkTheme: AppTheme.darkTheme,
      themeMode: themeMode,
      routerConfig: appRouter,
    );
  }
}
