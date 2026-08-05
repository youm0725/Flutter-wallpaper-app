import 'package:flutter/material.dart';

/// Centralized color palette for the application.
/// 
/// Designed with a minimal, timeless, and premium aesthetic
/// adhering to Material 3 neutral slate color principles.
abstract final class AppColors {
  // Primary Palette
  static const Color primary = Color(0xFF1E293B); // Deep Charcoal Slate
  static const Color onPrimary = Color(0xFFFFFFFF);
  static const Color primaryContainer = Color(0xFFF1F5F9);
  static const Color onPrimaryContainer = Color(0xFF0F172A);

  // Neutral Palette
  static const Color background = Color(0xFFF8FAFC); // Clean Light Slate Tint
  static const Color onBackground = Color(0xFF0F172A);
  static const Color surface = Color(0xFFFFFFFF); // Pure White
  static const Color onSurface = Color(0xFF0F172A);
  static const Color surfaceVariant = Color(0xFFF1F5F9);
  static const Color onSurfaceVariant = Color(0xFF475569);

  // Accent & Secondary
  static const Color secondary = Color(0xFF475569); // Slate Gray
  static const Color onSecondary = Color(0xFFFFFFFF);

  // Borders & Dividers
  static const Color border = Color(0xFFE2E8F0); // Subtle Border Tint
  static const Color divider = Color(0xFFCBD5E1);

  // States
  static const Color disabled = Color(0xFF94A3B8);
}
