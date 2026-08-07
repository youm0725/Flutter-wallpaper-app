import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../core/constants/app_sizes.dart';
import '../../core/router/route_constants.dart';
import '../../models/user_collection.dart';
import '../../models/user_preferences.dart';
import '../../models/wallpaper.dart';
import '../../providers/preferences_provider.dart';
import '../../providers/user_collection_provider.dart';
import '../../widgets/widgets.dart';

/// Screen displaying the contents of a specific user collection,
/// allowing wallpaper browsing, removing wallpapers from the collection,
/// renaming the collection, and deleting the collection.
class UserCollectionDetailsScreen extends ConsumerWidget {
  final String collectionId;

  const UserCollectionDetailsScreen({
    super.key,
    required this.collectionId,
  });

  void _showRenameDialog(
      BuildContext context, WidgetRef ref, UserCollection collection) {
    final controller = TextEditingController(text: collection.name);
    showDialog<void>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Rename Collection'),
        content: TextField(
          controller: controller,
          autofocus: true,
          decoration: const InputDecoration(hintText: 'Collection Name'),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () {
              final newName = controller.text.trim();
              if (newName.isNotEmpty) {
                ref
                    .read(userCollectionsNotifierProvider.notifier)
                    .renameCollection(collection.id, newName);
              }
              Navigator.pop(ctx);
            },
            child: const Text('Save'),
          ),
        ],
      ),
    );
  }

  Future<void> _deleteCollection(
      BuildContext context, WidgetRef ref, UserCollection collection) async {
    final confirmed = await ConfirmationDialog.show(
      context,
      title: 'Delete Collection?',
      message:
          'Are you sure you want to delete "${collection.name}"? This action cannot be undone.',
      confirmLabel: 'Delete',
      isDestructive: true,
    );

    if (confirmed == true) {
      await ref
          .read(userCollectionsNotifierProvider.notifier)
          .deleteCollection(collection.id);
      if (context.mounted) {
        context.pop();
      }
    }
  }

  Future<void> _removeWallpaper(BuildContext context, WidgetRef ref,
      UserCollection collection, Wallpaper wallpaper) async {
    await ref
        .read(userCollectionsNotifierProvider.notifier)
        .removeWallpaperFromCollection(collection.id, wallpaper.id);

    if (context.mounted) {
      ScaffoldMessenger.of(context).hideCurrentSnackBar();
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Removed "${wallpaper.title}" from collection'),
          behavior: SnackBarBehavior.floating,
          margin: const EdgeInsets.all(AppSizes.p16),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(AppSizes.radiusSm),
          ),
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final asyncCollections = ref.watch(userCollectionsNotifierProvider);
    final prefs =
        ref.watch(userPreferencesNotifierProvider).value ?? const UserPreferences();
    final crossAxisCount = calculateGridCrossAxisCount(context, prefs.gridDensity);

    final collections = asyncCollections.value ?? const <UserCollection>[];
    final collection = collections.firstWhere(
      (c) => c.id == collectionId,
      orElse: () => UserCollection(
        id: collectionId,
        name: 'Collection',
        createdDate: DateTime.now(),
        wallpaperIds: const [],
      ),
    );

    final wallpapers = ref.watch(userCollectionWallpapersProvider(collectionId));

    return Scaffold(
      appBar: AppBar(
        title: Text(collection.name),
        actions: [
          IconButton(
            icon: const Icon(Icons.edit_outlined),
            onPressed: () => _showRenameDialog(context, ref, collection),
            tooltip: 'Rename Collection',
          ),
          IconButton(
            icon: const Icon(Icons.delete_outline_rounded),
            onPressed: () => _deleteCollection(context, ref, collection),
            tooltip: 'Delete Collection',
          ),
        ],
      ),
      body: SafeArea(
        child: wallpapers.isEmpty
            ? EmptyStateView(
                icon: Icons.collections_bookmark_outlined,
                title: 'Collection is Empty',
                description:
                    'Tap the bookmark icon on any wallpaper to add it to "${collection.name}".',
                actionLabel: 'Browse Wallpapers',
                onAction: () => context.goNamed(RouteConstants.homeName),
              )
            : CustomScrollView(
                physics: const BouncingScrollPhysics(),
                slivers: [
                  SliverToBoxAdapter(
                    child: SectionHeader(
                      title: collection.name,
                      subtitle:
                          '${wallpapers.length} ${wallpapers.length == 1 ? 'wallpaper' : 'wallpapers'} in this collection',
                    ),
                  ),
                  SliverPadding(
                    padding: const EdgeInsets.symmetric(
                      horizontal: AppSizes.p16,
                      vertical: AppSizes.p8,
                    ),
                    sliver: SliverGrid(
                      gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
                        crossAxisCount: crossAxisCount,
                        mainAxisSpacing: AppSizes.p16,
                        crossAxisSpacing: AppSizes.p16,
                        childAspectRatio: 0.65,
                      ),
                      delegate: SliverChildBuilderDelegate(
                        (context, index) {
                          final wallpaper = wallpapers[index];
                          return Stack(
                            fit: StackFit.expand,
                            children: [
                              WallpaperCard(
                                wallpaper: wallpaper,
                                onTap: () {
                                  context.pushNamed(
                                    RouteConstants.wallpaperDetailsName,
                                    pathParameters: {'id': wallpaper.id},
                                    extra: wallpaper,
                                  );
                                },
                              ),

                              // Quick remove button overlay on top right
                              Positioned(
                                top: AppSizes.p6,
                                left: AppSizes.p6,
                                child: Material(
                                  color: Colors.black.withValues(alpha: 0.55),
                                  shape: const CircleBorder(),
                                  child: InkWell(
                                    customBorder: const CircleBorder(),
                                    onTap: () => _removeWallpaper(
                                        context, ref, collection, wallpaper),
                                    child: const Padding(
                                      padding: EdgeInsets.all(AppSizes.p6),
                                      child: Icon(
                                        Icons.remove_circle_outline_rounded,
                                        size: 16.0,
                                        color: Colors.white,
                                      ),
                                    ),
                                  ),
                                ),
                              ),
                            ],
                          );
                        },
                        childCount: wallpapers.length,
                      ),
                    ),
                  ),
                  const SliverToBoxAdapter(
                    child: SizedBox(height: AppSizes.p24),
                  ),
                ],
              ),
      ),
    );
  }
}
