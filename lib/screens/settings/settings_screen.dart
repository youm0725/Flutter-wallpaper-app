import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../core/constants/app_sizes.dart';
import '../../core/router/route_constants.dart';
import '../../providers/engagement_provider.dart';
import '../../providers/favorites_provider.dart';
import '../../providers/preferences_provider.dart';
import '../../providers/share_provider.dart';
import '../../providers/theme_provider.dart';
import '../../providers/user_collection_provider.dart';
import '../../widgets/widgets.dart';

/// Full Settings Screen — Appearance, Home Feed, Data, Engagement, and Backup sections.
class SettingsScreen extends ConsumerWidget {
  const SettingsScreen({super.key});

  static const int _currentBottomNavIndex = 2;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final asyncPrefs = ref.watch(userPreferencesNotifierProvider);
    final asyncTheme = ref.watch(themeModeProvider);
    final currentThemeMode = asyncTheme.value ?? ThemeMode.system;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Settings'),
        centerTitle: false,
      ),
      body: SafeArea(
        child: asyncPrefs.when(
          data: (prefs) => ListView(
            physics: const BouncingScrollPhysics(),
            padding: const EdgeInsets.symmetric(
              vertical: AppSizes.p8,
              horizontal: AppSizes.p4,
            ),
            children: [

              // ── 1. APPEARANCE ───────────────────────────────────────────
              _SettingsGroup(
                header: const SectionHeader(
                  title: 'Appearance',
                  subtitle: 'Theme and layout preferences',
                ),
                children: [
                  PreferenceTile(
                    icon: Icons.brightness_auto_rounded,
                    title: 'App Theme',
                    subtitle: _themeModeLabel(currentThemeMode),
                    trailing: ThemeSelector(
                      selectedMode: currentThemeMode,
                      onSelected: (mode) => ref
                          .read(themeModeProvider.notifier)
                          .setThemeMode(mode),
                    ),
                  ),
                  PreferenceTile(
                    icon: Icons.grid_view_rounded,
                    title: 'Grid Layout',
                    subtitle: 'Thumbnail density',
                    trailing: OptionSelector(
                      selectedDensity: prefs.gridDensity,
                      onSelected: (density) => ref
                          .read(userPreferencesNotifierProvider.notifier)
                          .setGridDensity(density),
                    ),
                  ),
                ],
              ),

              const SizedBox(height: AppSizes.p8),

              // ── 2. HOME FEED ────────────────────────────────────────────
              _SettingsGroup(
                header: const SectionHeader(
                  title: 'Home Feed',
                  subtitle: 'Toggle discovery sections',
                ),
                children: [
                  PreferenceTile(
                    icon: Icons.today_rounded,
                    title: 'Wallpaper of the Day',
                    subtitle: 'Daily hero banner',
                    trailing: Switch.adaptive(
                      value: prefs.showDailyWallpaper,
                      onChanged: (val) => ref
                          .read(userPreferencesNotifierProvider.notifier)
                          .toggleDailyWallpaper(val),
                    ),
                  ),
                  PreferenceTile(
                    icon: Icons.star_outline_rounded,
                    title: "Editor's Picks",
                    subtitle: 'Featured wallpapers',
                    trailing: Switch.adaptive(
                      value: prefs.showFeaturedSection,
                      onChanged: (val) => ref
                          .read(userPreferencesNotifierProvider.notifier)
                          .toggleFeaturedSection(val),
                    ),
                  ),
                  PreferenceTile(
                    icon: Icons.collections_bookmark_outlined,
                    title: 'Curated Collections',
                    subtitle: 'Themed gallery sections',
                    trailing: Switch.adaptive(
                      value: prefs.showCollectionsSection,
                      onChanged: (val) => ref
                          .read(userPreferencesNotifierProvider.notifier)
                          .toggleCollectionsSection(val),
                    ),
                  ),
                ],
              ),

              const SizedBox(height: AppSizes.p8),

              // ── 3. DATA & LIBRARY ───────────────────────────────────────
              _SettingsGroup(
                header: const SectionHeader(
                  title: 'Data & Library',
                  subtitle: 'Manage local offline data',
                ),
                children: [
                  PreferenceTile(
                    icon: Icons.folder_special_outlined,
                    title: 'Personal Collections',
                    subtitle: 'Manage custom libraries',
                    trailing: const Icon(Icons.chevron_right_rounded),
                    onTap: () => context
                        .pushNamed(RouteConstants.userCollectionsName),
                  ),
                  PreferenceTile(
                    icon: Icons.heart_broken_outlined,
                    title: 'Clear All Favorites',
                    subtitle: 'Remove saved wallpapers',
                    onTap: () => _clearFavorites(context, ref),
                  ),
                  PreferenceTile(
                    icon: Icons.folder_delete_outlined,
                    title: 'Delete All Collections',
                    subtitle: 'Remove personal libraries',
                    onTap: () => _deleteAllCollections(context, ref),
                  ),
                ],
              ),

              const SizedBox(height: AppSizes.p8),

              // ── 4. ABOUT & ENGAGEMENT ───────────────────────────────────
              _SettingsGroup(
                header: const SectionHeader(
                  title: 'About & Feedback',
                  subtitle: 'App info, ratings, and support',
                ),
                children: [
                  PreferenceTile(
                    icon: Icons.info_outline_rounded,
                    title: 'About Wallpaper Gallery',
                    subtitle: 'Version, privacy & licenses',
                    trailing: const Icon(Icons.chevron_right_rounded),
                    onTap: () =>
                        context.pushNamed(RouteConstants.aboutName),
                  ),
                  PreferenceTile(
                    icon: Icons.star_rate_rounded,
                    title: 'Rate the App',
                    subtitle: 'Share your experience on the store',
                    onTap: () => _rateApp(context, ref),
                  ),
                  PreferenceTile(
                    icon: Icons.rate_review_outlined,
                    title: 'Send Feedback',
                    subtitle: 'Help us improve',
                    onTap: () => _sendFeedback(context, ref),
                  ),
                  PreferenceTile(
                    icon: Icons.share_rounded,
                    title: 'Share the App',
                    subtitle: 'Recommend to friends',
                    onTap: () => shareApp(ref),
                  ),
                ],
              ),

              const SizedBox(height: AppSizes.p8),

              // ── 5. BACKUP & RESTORE ─────────────────────────────────────
              _SettingsGroup(
                header: const SectionHeader(
                  title: 'Backup & Restore',
                  subtitle: 'Offline data management',
                ),
                children: [
                  PreferenceTile(
                    icon: Icons.upload_file_outlined,
                    title: 'Export Backup',
                    subtitle: 'Generate offline JSON snapshot',
                    onTap: () => _exportBackup(context, ref, prefs),
                  ),
                  PreferenceTile(
                    icon: Icons.restore_page_outlined,
                    title: 'Reset All Preferences',
                    subtitle: 'Restore defaults',
                    onTap: () => _resetPreferences(context, ref),
                  ),
                ],
              ),

              const SizedBox(height: AppSizes.p32),
            ],
          ),
          loading: () =>
              const LoadingView(message: 'Loading settings...'),
          error: (error, _) =>
              ErrorStateView(message: error.toString()),
        ),
      ),
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _currentBottomNavIndex,
        onTap: (index) => _onBottomNavTapped(context, index),
        items: const [
          BottomNavigationBarItem(
            icon: Icon(Icons.home_outlined),
            activeIcon: Icon(Icons.home_rounded),
            label: 'Home',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.favorite_outline_rounded),
            activeIcon: Icon(Icons.favorite_rounded),
            label: 'Favorites',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.settings_outlined),
            activeIcon: Icon(Icons.settings_rounded),
            label: 'Settings',
          ),
        ],
      ),
    );
  }

  // ── Helpers ──────────────────────────────────────────────────────────────

  String _themeModeLabel(ThemeMode mode) => switch (mode) {
        ThemeMode.system => 'Follow system',
        ThemeMode.light => 'Light theme',
        ThemeMode.dark => 'Dark theme',
      };

  void _onBottomNavTapped(BuildContext context, int index) {
    if (index == _currentBottomNavIndex) return;
    if (index == 0) context.goNamed(RouteConstants.homeName);
    if (index == 1) context.goNamed(RouteConstants.favoritesName);
  }

  Future<void> _rateApp(BuildContext context, WidgetRef ref) async {
    await requestAppReview(ref);
  }

  Future<void> _sendFeedback(BuildContext context, WidgetRef ref) async {
    final success = await openFeedback(ref);
    if (!success && context.mounted) {
      _showSnackBar(context, 'No email app found. Please contact support.');
    }
  }

  Future<void> _clearFavorites(BuildContext context, WidgetRef ref) async {
    final confirmed = await ConfirmationDialog.show(
      context,
      title: 'Clear Favorites?',
      message: 'All saved favorite wallpapers will be removed.',
      confirmLabel: 'Clear All',
      isDestructive: true,
    );
    if (confirmed == true) {
      await ref.read(favoritesRepositoryProvider).clearFavorites();
      ref.invalidate(favoritesNotifierProvider);
      if (context.mounted) {
        _showSnackBar(context, 'Favorites cleared');
      }
    }
  }

  Future<void> _deleteAllCollections(
      BuildContext context, WidgetRef ref) async {
    final confirmed = await ConfirmationDialog.show(
      context,
      title: 'Delete All Collections?',
      message:
          'All personal wallpaper libraries will be permanently deleted.',
      confirmLabel: 'Delete All',
      isDestructive: true,
    );
    if (confirmed == true) {
      final collections =
          ref.read(userCollectionsNotifierProvider).value ?? [];
      for (final col in collections) {
        await ref
            .read(userCollectionsNotifierProvider.notifier)
            .deleteCollection(col.id);
      }
      if (context.mounted) {
        _showSnackBar(context, 'All collections deleted');
      }
    }
  }

  Future<void> _exportBackup(
      BuildContext context, WidgetRef ref, dynamic prefs) async {
    final favs =
        ref.read(favoritesNotifierProvider).value?.toList() ?? [];
    final userCols = ref
            .read(userCollectionsNotifierProvider)
            .value
            ?.map((c) => c.toJson())
            .toList() ??
        [];
    final currentPrefs =
        (prefs as dynamic).toJson() as Map<String, dynamic>;

    final backupService = ref.read(backupServiceProvider);
    final jsonStr = await backupService.exportBackupToJson(
      favorites: favs,
      userCollections: userCols,
      preferences: currentPrefs,
    );

    if (context.mounted) {
      showDialog<void>(
        context: context,
        builder: (ctx) => AlertDialog(
          title: const Text('Backup Exported'),
          content: SingleChildScrollView(
            child: SelectableText(
              jsonStr,
              style: const TextStyle(
                fontFamily: 'monospace',
                fontSize: 12.0,
              ),
            ),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(ctx),
              child: const Text('Close'),
            ),
          ],
        ),
      );
    }
  }

  Future<void> _resetPreferences(
      BuildContext context, WidgetRef ref) async {
    final confirmed = await ConfirmationDialog.show(
      context,
      title: 'Reset Preferences?',
      message:
          'All layout and view preferences will be restored to defaults.',
      confirmLabel: 'Reset',
    );
    if (confirmed == true) {
      await ref
          .read(userPreferencesNotifierProvider.notifier)
          .resetAll();
      if (context.mounted) {
        _showSnackBar(context, 'Preferences reset to default');
      }
    }
  }

  void _showSnackBar(BuildContext context, String message) {
    ScaffoldMessenger.of(context).hideCurrentSnackBar();
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        behavior: SnackBarBehavior.floating,
        margin: const EdgeInsets.all(AppSizes.p16),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(AppSizes.radiusSm),
        ),
      ),
    );
  }
}

// ── Private Layout Widget ────────────────────────────────────────────────────

/// Wraps a settings group with its header and subtle card surface.
class _SettingsGroup extends StatelessWidget {
  final Widget header;
  final List<Widget> children;

  const _SettingsGroup({required this.header, required this.children});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        header,
        Container(
          margin: const EdgeInsets.symmetric(
            horizontal: AppSizes.p12,
            vertical: AppSizes.p4,
          ),
          decoration: BoxDecoration(
            color: theme.colorScheme.surfaceContainerLowest,
            borderRadius: BorderRadius.circular(AppSizes.radiusMd),
            border: Border.all(
              color: theme.colorScheme.outlineVariant.withValues(alpha: 0.5),
            ),
          ),
          child: Column(
            children: _separatedChildren(children, theme),
          ),
        ),
      ],
    );
  }

  List<Widget> _separatedChildren(List<Widget> items, ThemeData theme) {
    if (items.isEmpty) return [];
    final result = <Widget>[];
    for (var i = 0; i < items.length; i++) {
      result.add(items[i]);
      if (i < items.length - 1) {
        result.add(Divider(
          height: 1,
          indent: AppSizes.p16 + 36 + AppSizes.p16, // align with tile content
          endIndent: AppSizes.p16,
          color: theme.colorScheme.outlineVariant.withValues(alpha: 0.4),
        ));
      }
    }
    return result;
  }
}
