import 'dart:convert';
import 'package:flutter/services.dart';
import '../models/wallpaper.dart';
import '../services/asset_service.dart';

/// Contract for wallpaper data repository operations.
abstract interface class IWallpaperRepository {
  Future<List<Wallpaper>> getWallpapers();
  Future<Wallpaper?> getWallpaperById(String id);
  Future<List<Wallpaper>> getWallpapersByCategory(String category);
}

/// Production implementation of [IWallpaperRepository] discovering WebP assets directly.
final class LocalWallpaperRepository implements IWallpaperRepository {
  final IAssetService assetService;

  const LocalWallpaperRepository({
    required this.assetService,
  });

  @override
  Future<List<Wallpaper>> getWallpapers() async {
    try {
      final List<String> paths = await _getWallpaperAssetPaths();
      final wallpapers = <Wallpaper>[];

      for (final path in paths) {
        final filename = path.split('/').last;
        final lastDotIndex = filename.lastIndexOf('.');
        final stem = lastDotIndex != -1 ? filename.substring(0, lastDotIndex) : filename;
        final id = stem;

        // Parse category from prefix before underscore/dash, e.g. "nature_001" -> "Nature"
        String category = 'General';
        final parts = stem.split(RegExp(r'[_\-]'));
        if (parts.isNotEmpty && parts.first.isNotEmpty) {
          final rawCat = parts.first;
          if (!RegExp(r'^\d+$').hasMatch(rawCat)) {
            category = rawCat[0].toUpperCase() + rawCat.substring(1).toLowerCase();
          }
        }

        // Generate clean display title
        final words = stem.split(RegExp(r'[_\-]')).where((w) => w.isNotEmpty);
        final title = words
            .map((w) => w[0].toUpperCase() + w.substring(1).toLowerCase())
            .join(' ');

        wallpapers.add(
          Wallpaper(
            id: id,
            title: title.isEmpty ? stem : title,
            category: category,
            imagePath: path,
            resolution: '1080x1920',
            fileSize: '',
            tags: <String>[category.toLowerCase()],
          ),
        );
      }

      return wallpapers;
    } catch (_) {
      return const <Wallpaper>[];
    }
  }

  Future<List<String>> _getWallpaperAssetPaths() async {
    try {
      final manifestJson = await rootBundle.loadString('AssetManifest.json');
      final Map<String, dynamic> manifestMap = jsonDecode(manifestJson);
      final paths = manifestMap.keys
          .where((String k) => k.startsWith('assets/wallpapers/') && k.toLowerCase().endsWith('.webp'))
          .toList()..sort();
      return paths;
    } catch (_) {
      try {
        final manifest = await AssetManifest.loadFromAssetBundle(rootBundle);
        final paths = manifest
            .listAssets()
            .where((String k) => k.startsWith('assets/wallpapers/') && k.toLowerCase().endsWith('.webp'))
            .toList()..sort();
        return paths;
      } catch (_) {
        return const <String>[];
      }
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
}
