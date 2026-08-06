import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';
import '../models/user_collection.dart';

/// Repository interface for user custom wallpaper collections.
abstract interface class IUserCollectionRepository {
  Future<List<UserCollection>> getUserCollections();
  Future<UserCollection> createCollection(String name);
  Future<void> renameCollection(String collectionId, String newName);
  Future<void> deleteCollection(String collectionId);
  Future<void> addWallpaperToCollection(String collectionId, String wallpaperId);
  Future<void> removeWallpaperFromCollection(String collectionId, String wallpaperId);
}

/// Production implementation of [IUserCollectionRepository] persisting JSON via [SharedPreferences].
final class LocalUserCollectionRepository implements IUserCollectionRepository {
  static const String _key = 'user_collections_key';

  const LocalUserCollectionRepository();

  @override
  Future<List<UserCollection>> getUserCollections() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final jsonList = prefs.getStringList(_key) ?? <String>[];

      return jsonList.map((jsonStr) {
        final Map<String, dynamic> map =
            jsonDecode(jsonStr) as Map<String, dynamic>;
        return UserCollection.fromJson(map);
      }).toList(growable: false);
    } catch (_) {
      return const <UserCollection>[];
    }
  }

  @override
  Future<UserCollection> createCollection(String name) async {
    final collections = await getUserCollections();
    final newCollection = UserCollection(
      id: 'uc_${DateTime.now().millisecondsSinceEpoch}',
      name: name.trim(),
      createdDate: DateTime.now(),
      wallpaperIds: const <String>[],
    );

    final updatedList = <UserCollection>[...collections, newCollection];
    await _saveCollections(updatedList);
    return newCollection;
  }

  @override
  Future<void> renameCollection(String collectionId, String newName) async {
    final collections = await getUserCollections();
    final updatedList = collections.map((col) {
      if (col.id == collectionId) {
        return col.copyWith(name: newName.trim());
      }
      return col;
    }).toList();

    await _saveCollections(updatedList);
  }

  @override
  Future<void> deleteCollection(String collectionId) async {
    final collections = await getUserCollections();
    final updatedList =
        collections.where((col) => col.id != collectionId).toList();
    await _saveCollections(updatedList);
  }

  @override
  Future<void> addWallpaperToCollection(
      String collectionId, String wallpaperId) async {
    final collections = await getUserCollections();
    final updatedList = collections.map((col) {
      if (col.id == collectionId) {
        if (!col.wallpaperIds.contains(wallpaperId)) {
          return col.copyWith(
            wallpaperIds: <String>[...col.wallpaperIds, wallpaperId],
          );
        }
      }
      return col;
    }).toList();

    await _saveCollections(updatedList);
  }

  @override
  Future<void> removeWallpaperFromCollection(
      String collectionId, String wallpaperId) async {
    final collections = await getUserCollections();
    final updatedList = collections.map((col) {
      if (col.id == collectionId) {
        return col.copyWith(
          wallpaperIds:
              col.wallpaperIds.where((id) => id != wallpaperId).toList(),
        );
      }
      return col;
    }).toList();

    await _saveCollections(updatedList);
  }

  Future<void> _saveCollections(List<UserCollection> list) async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final jsonList =
          list.map((col) => jsonEncode(col.toJson())).toList(growable: false);
      await prefs.setStringList(_key, jsonList);
    } catch (_) {}
  }
}
