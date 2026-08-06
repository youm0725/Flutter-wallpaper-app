import 'package:shared_preferences/shared_preferences.dart';

/// Repository interface for recently viewed wallpaper history.
abstract interface class IRecentlyViewedRepository {
  Future<List<String>> getRecentlyViewedIds();
  Future<void> addRecentlyViewedId(String wallpaperId);
  Future<void> clearRecentlyViewed();
}

/// Production implementation of [IRecentlyViewedRepository] using [SharedPreferences].
final class LocalRecentlyViewedRepository implements IRecentlyViewedRepository {
  static const String _key = 'recently_viewed_ids_key';
  static const int _maxItems = 20;

  const LocalRecentlyViewedRepository();

  @override
  Future<List<String>> getRecentlyViewedIds() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      return prefs.getStringList(_key) ?? const <String>[];
    } catch (_) {
      return const <String>[];
    }
  }

  @override
  Future<void> addRecentlyViewedId(String wallpaperId) async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final current = prefs.getStringList(_key) ?? <String>[];

      final updated = <String>[
        wallpaperId,
        ...current.where((id) => id != wallpaperId),
      ].take(_maxItems).toList();

      await prefs.setStringList(_key, updated);
    } catch (_) {}
  }

  @override
  Future<void> clearRecentlyViewed() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.remove(_key);
    } catch (_) {}
  }
}
