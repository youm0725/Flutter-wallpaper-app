import 'dart:convert';
import '../models/category.dart';
import '../services/asset_service.dart';

/// Contract for fetching wallpaper categories metadata.
abstract interface class ICategoryRepository {
  Future<List<Category>> getCategories();
}

/// Production implementation of [ICategoryRepository] loading from assets/metadata/categories.json.
final class LocalCategoryRepository implements ICategoryRepository {
  static const String _categoriesMetadataPath = 'assets/metadata/categories.json';
  final IAssetService assetService;

  const LocalCategoryRepository({
    required this.assetService,
  });

  @override
  Future<List<Category>> getCategories() async {
    try {
      final jsonString = await assetService.loadString(_categoriesMetadataPath);
      if (jsonString.trim().isEmpty) {
        return const <Category>[];
      }

      final dynamic decoded = jsonDecode(jsonString);
      if (decoded is! List) {
        return const <Category>[];
      }

      return decoded
          .whereType<Map<String, dynamic>>()
          .map(Category.fromJson)
          .toList(growable: false);
    } catch (_) {
      return const <Category>[];
    }
  }
}
