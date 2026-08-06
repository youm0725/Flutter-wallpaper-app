import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'package:wallpaper_app/main.dart';

void main() {
  testWidgets('WallpaperApp smoke test', (WidgetTester tester) async {
    // Build our app and trigger a frame.
    await tester.pumpWidget(
      const ProviderScope(
        child: WallpaperApp(),
      ),
    );

    // Verify that the splash screen shows 'Wallpaper Gallery'.
    expect(find.text('Wallpaper Gallery'), findsOneWidget);
  });
}

