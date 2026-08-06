import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../core/constants/app_sizes.dart';
import '../models/wallpaper.dart';
import '../providers/user_collection_provider.dart';

/// Modal bottom sheet for adding a wallpaper to a user collection or creating a new collection.
class AddToCollectionSheet extends ConsumerStatefulWidget {
  final Wallpaper wallpaper;

  const AddToCollectionSheet({
    super.key,
    required this.wallpaper,
  });

  static void show(BuildContext context, Wallpaper wallpaper) {
    showModalBottomSheet<void>(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (context) => AddToCollectionSheet(wallpaper: wallpaper),
    );
  }

  @override
  ConsumerState<AddToCollectionSheet> createState() =>
      _AddToCollectionSheetState();
}

class _AddToCollectionSheetState
    extends ConsumerState<AddToCollectionSheet> {
  final TextEditingController _nameController = TextEditingController();
  bool _isCreating = false;

  @override
  void dispose() {
    _nameController.dispose();
    super.dispose();
  }

  Future<void> _handleCreateCollection() async {
    final name = _nameController.text.trim();
    if (name.isEmpty) return;

    final newCol = await ref
        .read(userCollectionsNotifierProvider.notifier)
        .createCollection(name);

    if (newCol != null) {
      await ref
          .read(userCollectionsNotifierProvider.notifier)
          .addWallpaperToCollection(newCol.id, widget.wallpaper.id);
    }

    _nameController.clear();
    setState(() {
      _isCreating = false;
    });

    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Added to collection "$name"'),
          behavior: SnackBarBehavior.floating,
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final asyncCollections = ref.watch(userCollectionsNotifierProvider);

    return Container(
      padding: EdgeInsets.only(
        bottom: MediaQuery.of(context).viewInsets.bottom + AppSizes.p16,
        top: AppSizes.p16,
        left: AppSizes.p16,
        right: AppSizes.p16,
      ),
      decoration: BoxDecoration(
        color: theme.scaffoldBackgroundColor,
        borderRadius: const BorderRadius.vertical(
          top: Radius.circular(AppSizes.radiusLg),
        ),
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Center(
            child: Container(
              width: 40.0,
              height: 4.0,
              decoration: BoxDecoration(
                color: theme.colorScheme.outline.withValues(alpha: 0.4),
                borderRadius: BorderRadius.circular(2.0),
              ),
            ),
          ),
          const SizedBox(height: AppSizes.p16),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                'Save to Collection',
                style: theme.textTheme.titleMedium?.copyWith(
                  fontWeight: FontWeight.w700,
                ),
              ),
              IconButton(
                icon: const Icon(Icons.add_rounded),
                onPressed: () {
                  setState(() {
                    _isCreating = !_isCreating;
                  });
                },
                tooltip: 'Create Collection',
              ),
            ],
          ),
          if (_isCreating) ...[
            const SizedBox(height: AppSizes.p8),
            Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _nameController,
                    autofocus: true,
                    decoration: InputDecoration(
                      hintText: 'Collection name (e.g. Dream Setup)',
                      isDense: true,
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(AppSizes.radiusSm),
                      ),
                    ),
                  ),
                ),
                const SizedBox(width: AppSizes.p8),
                ElevatedButton(
                  onPressed: _handleCreateCollection,
                  child: const Text('Save'),
                ),
              ],
            ),
            const SizedBox(height: AppSizes.p12),
          ],
          const Divider(),
          asyncCollections.when(
            data: (collections) {
              if (collections.isEmpty) {
                return Padding(
                  padding: const EdgeInsets.symmetric(vertical: AppSizes.p24),
                  child: Center(
                    child: Column(
                      children: [
                        Icon(
                          Icons.collections_bookmark_outlined,
                          size: AppSizes.iconLg,
                          color: theme.colorScheme.onSurfaceVariant
                              .withValues(alpha: 0.4),
                        ),
                        const SizedBox(height: AppSizes.p8),
                        Text(
                          'No collections created yet.',
                          style: theme.textTheme.bodyMedium?.copyWith(
                            color: theme.colorScheme.onSurfaceVariant,
                          ),
                        ),
                        const SizedBox(height: AppSizes.p8),
                        TextButton(
                          onPressed: () {
                            setState(() {
                              _isCreating = true;
                            });
                          },
                          child: const Text('Create your first collection'),
                        ),
                      ],
                    ),
                  ),
                );
              }

              return ListView.builder(
                shrinkWrap: true,
                physics: const NeverScrollableScrollPhysics(),
                itemCount: collections.length,
                itemBuilder: (context, index) {
                  final col = collections[index];
                  final isInCollection =
                      col.wallpaperIds.contains(widget.wallpaper.id);

                  return CheckboxListTile(
                    title: Text(
                      col.name,
                      style: theme.textTheme.bodyMedium?.copyWith(
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                    subtitle: Text('${col.wallpaperIds.length} wallpapers'),
                    value: isInCollection,
                    onChanged: (bool? checked) async {
                      if (checked == true) {
                        await ref
                            .read(userCollectionsNotifierProvider.notifier)
                            .addWallpaperToCollection(
                                col.id, widget.wallpaper.id);
                      } else {
                        await ref
                            .read(userCollectionsNotifierProvider.notifier)
                            .removeWallpaperFromCollection(
                                col.id, widget.wallpaper.id);
                      }
                    },
                  );
                },
              );
            },
            loading: () => const Center(
              child: Padding(
                padding: EdgeInsets.all(AppSizes.p24),
                child: CircularProgressIndicator(),
              ),
            ),
            error: (error, stack) => const SizedBox.shrink(),
          ),
          const SizedBox(height: AppSizes.p16),
        ],
      ),
    );
  }
}
