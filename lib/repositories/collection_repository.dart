import 'dart:convert';
import '../models/collection.dart';
import '../services/asset_service.dart';

/// Repository interface for fetching curated wallpaper collections.
abstract interface class ICollectionRepository {
  Future<List<Collection>> getCollections();
}

/// Production implementation of [ICollectionRepository] loading from local JSON asset.
final class LocalCollectionRepository implements ICollectionRepository {
  final IAssetService assetService;

  const LocalCollectionRepository({
    required this.assetService,
  });

  @override
  Future<List<Collection>> getCollections() async {
    try {
      final jsonString =
          await assetService.loadString('assets/metadata/collections.json');
      final dynamic decoded = jsonDecode(jsonString);

      if (decoded is! List) {
        return const <Collection>[];
      }

      return decoded
          .whereType<Map<String, dynamic>>()
          .map(Collection.fromJson)
          .toList(growable: false);
    } catch (_) {
      return const <Collection>[];
    }
  }
}
