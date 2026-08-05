import 'dart:convert';
import 'package:flutter/foundation.dart';
import '../models/wallpaper.dart';
import '../services/asset_service.dart';

/// Contract for wallpaper data repository operations.
abstract interface class IWallpaperRepository {
  Future<List<Wallpaper>> getWallpapers();
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
}
