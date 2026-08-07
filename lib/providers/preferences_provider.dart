import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/user_preferences.dart';
import '../repositories/preferences_repository.dart';
import '../services/backup_service.dart';

/// Provider for [IPreferencesRepository] instance.
final preferencesRepositoryProvider = Provider<IPreferencesRepository>((ref) {
  return const LocalPreferencesRepository();
});

/// Provider for [IBackupService] instance.
final backupServiceProvider = Provider<IBackupService>((ref) {
  return const LocalBackupService();
});

/// AsyncNotifier managing active user preferences.
class UserPreferencesNotifier extends AsyncNotifier<UserPreferences> {
  @override
  Future<UserPreferences> build() async {
    final repository = ref.watch(preferencesRepositoryProvider);
    return repository.getPreferences();
  }

  Future<void> setGridDensity(GridDensity density) async {
    final current = state.value ?? const UserPreferences();
    final updated = current.copyWith(gridDensity: density);
    state = AsyncData(updated);

    final repository = ref.read(preferencesRepositoryProvider);
    await repository.savePreferences(updated);
  }

  Future<void> resetAll() async {
    const defaultPrefs = UserPreferences();
    state = const AsyncData(defaultPrefs);

    final repository = ref.read(preferencesRepositoryProvider);
    await repository.resetPreferences();
  }
}

/// Provider for active [UserPreferences] state.
final userPreferencesNotifierProvider =
    AsyncNotifierProvider<UserPreferencesNotifier, UserPreferences>(
  UserPreferencesNotifier.new,
);

/// Helper function to calculate responsive grid column count based on [GridDensity] and screen width.
int calculateGridCrossAxisCount(BuildContext context, GridDensity density) {
  final width = MediaQuery.of(context).size.width;

  switch (density) {
    case GridDensity.compact:
      if (width > 900) return 5;
      if (width > 600) return 4;
      return 3;
    case GridDensity.comfortable:
      if (width > 900) return 4;
      if (width > 600) return 3;
      return 2;
    case GridDensity.large:
      if (width > 900) return 3;
      if (width > 600) return 2;
      return 1;
  }
}
