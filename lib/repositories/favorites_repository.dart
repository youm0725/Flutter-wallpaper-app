import 'package:shared_preferences/shared_preferences.dart';

/// Repository interface for favorite wallpapers local storage.
abstract interface class IFavoritesRepository {
  Future<List<String>> getFavoriteIds();
  Future<void> addFavorite(String wallpaperId);
  Future<void> removeFavorite(String wallpaperId);
  Future<bool> isFavorite(String wallpaperId);
  Future<void> clearFavorites();
}

/// Production implementation of [IFavoritesRepository] storing IDs via [SharedPreferences].
final class LocalFavoritesRepository implements IFavoritesRepository {
  static const String _key = 'favorites_ids_key';

  const LocalFavoritesRepository();

  @override
  Future<List<String>> getFavoriteIds() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      return prefs.getStringList(_key) ?? const <String>[];
    } catch (_) {
      return const <String>[];
    }
  }

  @override
  Future<void> addFavorite(String wallpaperId) async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final current = prefs.getStringList(_key) ?? <String>[];
      if (!current.contains(wallpaperId)) {
        final updated = <String>[...current, wallpaperId];
        await prefs.setStringList(_key, updated);
      }
    } catch (_) {}
  }

  @override
  Future<void> removeFavorite(String wallpaperId) async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final current = prefs.getStringList(_key) ?? <String>[];
      if (current.contains(wallpaperId)) {
        final updated = current.where((id) => id != wallpaperId).toList();
        await prefs.setStringList(_key, updated);
      }
    } catch (_) {}
  }

  @override
  Future<bool> isFavorite(String wallpaperId) async {
    final ids = await getFavoriteIds();
    return ids.contains(wallpaperId);
  }

  @override
  Future<void> clearFavorites() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.remove(_key);
    } catch (_) {}
  }
}
