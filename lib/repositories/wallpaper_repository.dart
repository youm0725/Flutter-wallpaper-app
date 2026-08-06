import 'dart:convert';
import 'package:flutter/foundation.dart';
import '../models/wallpaper.dart';
import '../services/asset_service.dart';

/// Contract for wallpaper data repository operations.
abstract interface class IWallpaperRepository {
  Future<List<Wallpaper>> getWallpapers();
  Future<Wallpaper?> getWallpaperById(String id);
  Future<List<Wallpaper>> getWallpapersByCategory(String category);
  Future<List<Wallpaper>> getFeaturedWallpapers();
}

/// Local offline implementation of [IWallpaperRepository].
final class LocalWallpaperRepository implements IWallpaperRepository {
  static const String _metadataAssetPath = 'assets/metadata/wallpapers.json';
  final IAssetService assetService;

  const LocalWallpaperRepository({
    required this.assetService,
  });

  @override
  Future<List<Wallpaper>> getWallpapers() async {
    try {
      final jsonString = await assetService.loadString(_metadataAssetPath);

      if (jsonString.trim().isEmpty) {
        return const <Wallpaper>[];
      }

      final dynamic decoded = jsonDecode(jsonString);

      if (decoded is! List) {
        throw FormatException(
          'Invalid JSON structure in $_metadataAssetPath. Expected a List.',
        );
      }

      final wallpapers = decoded
          .whereType<Map<String, dynamic>>()
          .map((jsonMap) => Wallpaper.fromJson(jsonMap))
          .toList(growable: false);

      return wallpapers;
    } catch (e, stackTrace) {
      if (kDebugMode) {
        debugPrint('Error loading wallpapers from metadata: $e\n$stackTrace');
      }
      rethrow;
    }
  }

  @override
  Future<Wallpaper?> getWallpaperById(String id) async {
    final wallpapers = await getWallpapers();
    try {
      return wallpapers.firstWhere((w) => w.id == id);
    } catch (_) {
      return null;
    }
  }

  @override
  Future<List<Wallpaper>> getWallpapersByCategory(String category) async {
    final wallpapers = await getWallpapers();
    final lowerCategory = category.toLowerCase().trim();
    return wallpapers
        .where((w) => w.category.toLowerCase().trim() == lowerCategory)
        .toList();
  }

  @override
  Future<List<Wallpaper>> getFeaturedWallpapers() async {
    final wallpapers = await getWallpapers();
    return wallpapers.where((w) => w.isFeatured).toList();
  }
}
