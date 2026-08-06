import 'package:flutter/material.dart';

/// Centralized color palette for the application.
/// 
/// Designed with a minimal, timeless, and premium aesthetic
/// adhering to Material 3 neutral slate color principles.
abstract final class AppColors {
  // Light Palette
  static const Color primary = Color(0xFF0F172A); // Obsidian Slate
  static const Color onPrimary = Color(0xFFFFFFFF);
  static const Color primaryContainer = Color(0xFFF1F5F9);
  static const Color onPrimaryContainer = Color(0xFF0F172A);

  static const Color background = Color(0xFFF8FAFC); // Light Slate Tint
  static const Color onBackground = Color(0xFF0F172A);
  static const Color surface = Color(0xFFFFFFFF); // Pure White
  static const Color onSurface = Color(0xFF0F172A);
  static const Color surfaceVariant = Color(0xFFF1F5F9);
  static const Color onSurfaceVariant = Color(0xFF64748B);

  static const Color secondary = Color(0xFF475569); // Slate Gray
  static const Color onSecondary = Color(0xFFFFFFFF);

  static const Color border = Color(0xFFE2E8F0); // Subtle Light Border
  static const Color divider = Color(0xFFCBD5E1);

  // Dark Palette
  static const Color darkPrimary = Color(0xFFF8FAFC); // Clean White/Light Slate
  static const Color darkOnPrimary = Color(0xFF0F172A);
  static const Color darkPrimaryContainer = Color(0xFF1E293B);
  static const Color darkOnPrimaryContainer = Color(0xFFF8FAFC);

  static const Color darkBackground = Color(0xFF0F172A); // Midnight Obsidian
  static const Color darkOnBackground = Color(0xFFF8FAFC);
  static const Color darkSurface = Color(0xFF1E293B); // Dark Slate Surface
  static const Color darkOnSurface = Color(0xFFF8FAFC);
  static const Color darkSurfaceVariant = Color(0xFF334155);
  static const Color darkOnSurfaceVariant = Color(0xFF94A3B8);

  static const Color darkSecondary = Color(0xFF94A3B8);
  static const Color darkOnSecondary = Color(0xFF0F172A);

  static const Color darkBorder = Color(0xFF334155); // Subtle Dark Border
  static const Color darkDivider = Color(0xFF334155);

  // States
  static const Color disabled = Color(0xFF94A3B8);
}
