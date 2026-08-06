import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/user_collection.dart';
import '../models/wallpaper.dart';
import '../repositories/user_collection_repository.dart';
import 'wallpaper_providers.dart';

/// Provider for [IUserCollectionRepository] instance.
final userCollectionRepositoryProvider =
    Provider<IUserCollectionRepository>((ref) {
  return const LocalUserCollectionRepository();
});

/// AsyncNotifier managing user custom collections list.
class UserCollectionsNotifier extends AsyncNotifier<List<UserCollection>> {
  @override
  Future<List<UserCollection>> build() async {
    final repository = ref.watch(userCollectionRepositoryProvider);
    return repository.getUserCollections();
  }

  Future<UserCollection?> createCollection(String name) async {
    if (name.trim().isEmpty) return null;
    final repository = ref.read(userCollectionRepositoryProvider);
    final newCol = await repository.createCollection(name);

    final current = state.value ?? const <UserCollection>[];
    state = AsyncData([...current, newCol]);
    return newCol;
  }

  Future<void> renameCollection(String collectionId, String newName) async {
    final repository = ref.read(userCollectionRepositoryProvider);
    await repository.renameCollection(collectionId, newName);

    final current = state.value ?? const <UserCollection>[];
    state = AsyncData(current.map((c) {
      if (c.id == collectionId) {
        return c.copyWith(name: newName.trim());
      }
      return c;
    }).toList());
  }

  Future<void> deleteCollection(String collectionId) async {
    final repository = ref.read(userCollectionRepositoryProvider);
    await repository.deleteCollection(collectionId);

    final current = state.value ?? const <UserCollection>[];
    state = AsyncData(current.where((c) => c.id != collectionId).toList());
  }

  Future<void> addWallpaperToCollection(
      String collectionId, String wallpaperId) async {
    final repository = ref.read(userCollectionRepositoryProvider);
    await repository.addWallpaperToCollection(collectionId, wallpaperId);

    final current = state.value ?? const <UserCollection>[];
    state = AsyncData(current.map((c) {
      if (c.id == collectionId) {
        if (!c.wallpaperIds.contains(wallpaperId)) {
          return c.copyWith(wallpaperIds: [...c.wallpaperIds, wallpaperId]);
        }
      }
      return c;
    }).toList());
  }

  Future<void> removeWallpaperFromCollection(
      String collectionId, String wallpaperId) async {
    final repository = ref.read(userCollectionRepositoryProvider);
    await repository.removeWallpaperFromCollection(collectionId, wallpaperId);

    final current = state.value ?? const <UserCollection>[];
    state = AsyncData(current.map((c) {
      if (c.id == collectionId) {
        return c.copyWith(
          wallpaperIds: c.wallpaperIds.where((id) => id != wallpaperId).toList(),
        );
      }
      return c;
    }).toList());
  }
}

/// Provider for user-created custom collections.
final userCollectionsNotifierProvider =
    AsyncNotifierProvider<UserCollectionsNotifier, List<UserCollection>>(
  UserCollectionsNotifier.new,
);

/// Family provider getting list of [Wallpaper] objects for a specific user collection ID.
final userCollectionWallpapersProvider =
    Provider.family<List<Wallpaper>, String>((ref, collectionId) {
  final asyncCollections = ref.watch(userCollectionsNotifierProvider);
  final asyncWallpapers = ref.watch(wallpapersProvider);

  final collections = asyncCollections.value ?? const <UserCollection>[];
  final targetCol = collections.firstWhere(
    (c) => c.id == collectionId,
    orElse: () => UserCollection(
      id: collectionId,
      name: '',
      createdDate: DateTime.now(),
      wallpaperIds: const [],
    ),
  );

  if (targetCol.wallpaperIds.isEmpty) return const <Wallpaper>[];

  return asyncWallpapers.when(
    data: (wallpapers) {
      final idsSet = targetCol.wallpaperIds.toSet();
      return wallpapers.where((w) => idsSet.contains(w.id)).toList();
    },
    loading: () => const <Wallpaper>[],
    error: (error, stack) => const <Wallpaper>[],
  );
});
