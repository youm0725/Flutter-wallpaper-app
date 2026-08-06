import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/constants/app_sizes.dart';
import '../../providers/user_collection_provider.dart';
import '../../widgets/widgets.dart';

/// Screen displaying user-created custom wallpaper collections.
class UserCollectionsScreen extends ConsumerWidget {
  const UserCollectionsScreen({super.key});

  void _showCreateDialog(BuildContext context, WidgetRef ref) {
    final controller = TextEditingController();
    showDialog<void>(
      context: context,
      builder: (context) {
        return AlertDialog(
          title: const Text('Create New Collection'),
          content: TextField(
            controller: controller,
            autofocus: true,
            decoration: const InputDecoration(
              hintText: 'Collection Name (e.g. Dream Setup)',
            ),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('Cancel'),
            ),
            ElevatedButton(
              onPressed: () {
                final name = controller.text.trim();
                if (name.isNotEmpty) {
                  ref
                      .read(userCollectionsNotifierProvider.notifier)
                      .createCollection(name);
                }
                Navigator.pop(context);
              },
              child: const Text('Create'),
            ),
          ],
        );
      },
    );
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final asyncCollections = ref.watch(userCollectionsNotifierProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('My Collections'),
        actions: [
          IconButton(
            icon: const Icon(Icons.add_rounded),
            onPressed: () => _showCreateDialog(context, ref),
            tooltip: 'New Collection',
          ),
        ],
      ),
      body: SafeArea(
        child: asyncCollections.when(
          data: (collections) {
            if (collections.isEmpty) {
              return EmptyStateView(
                icon: Icons.collections_bookmark_outlined,
                title: 'No User Collections Yet',
                description:
                    'Organize your favorite wallpapers into personal custom collections.',
                actionLabel: 'Create Collection',
                onAction: () => _showCreateDialog(context, ref),
              );
            }

            final crossAxisCount = _calculateCrossAxisCount(context);

            return CustomScrollView(
              physics: const BouncingScrollPhysics(),
              slivers: [
                const SliverToBoxAdapter(
                  child: SectionHeader(
                    title: 'Your Personal Libraries',
                    subtitle: 'Manage and view your custom collections',
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
                      childAspectRatio: 1.35,
                    ),
                    delegate: SliverChildBuilderDelegate(
                      (context, index) {
                        final col = collections[index];
                        return UserCollectionCard(
                          collection: col,
                          onTap: () {
                            // Can open collection detail or filter view
                          },
                        );
                      },
                      childCount: collections.length,
                    ),
                  ),
                ),
              ],
            );
          },
          loading: () => const LoadingView(message: 'Loading collections...'),
          error: (error, stack) => ErrorStateView(message: error.toString()),
        ),
      ),
    );
  }

  int _calculateCrossAxisCount(BuildContext context) {
    final width = MediaQuery.of(context).size.width;
    if (width > 900) return 4;
    if (width > 600) return 3;
    return 2;
  }
}
