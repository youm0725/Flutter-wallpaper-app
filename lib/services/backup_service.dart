import 'dart:convert';
import 'package:flutter/foundation.dart';

/// Immutable model representing complete local user data backup package.
@immutable
final class UserDataBackup {
  final List<String> favorites;
  final List<Map<String, dynamic>> userCollections;
  final Map<String, dynamic> preferences;
  final String exportedAt;

  const UserDataBackup({
    required this.favorites,
    required this.userCollections,
    required this.preferences,
    required this.exportedAt,
  });

  factory UserDataBackup.fromJson(Map<String, dynamic> json) {
    return UserDataBackup(
      favorites: (json['favorites'] as List<dynamic>?)
              ?.map((dynamic e) => e.toString())
              .toList() ??
          const <String>[],
      userCollections: (json['userCollections'] as List<dynamic>?)
              ?.whereType<Map<String, dynamic>>()
              .toList() ??
          const <Map<String, dynamic>>[],
      preferences: json['preferences'] as Map<String, dynamic>? ??
          const <String, dynamic>{},
      exportedAt: json['exportedAt'] as String? ?? '',
    );
  }

  Map<String, dynamic> toJson() {
    return <String, dynamic>{
      'version': '1.0',
      'favorites': favorites,
      'userCollections': userCollections,
      'preferences': preferences,
      'exportedAt': exportedAt,
    };
  }
}

/// Backup service contract for local user data JSON export and import.
abstract interface class IBackupService {
  Future<String> exportBackupToJson({
    required List<String> favorites,
    required List<Map<String, dynamic>> userCollections,
    required Map<String, dynamic> preferences,
  });

  UserDataBackup? parseBackupFromJson(String jsonString);
}

/// Production implementation of [IBackupService].
final class LocalBackupService implements IBackupService {
  const LocalBackupService();

  @override
  Future<String> exportBackupToJson({
    required List<String> favorites,
    required List<Map<String, dynamic>> userCollections,
    required Map<String, dynamic> preferences,
  }) async {
    final backup = UserDataBackup(
      favorites: favorites,
      userCollections: userCollections,
      preferences: preferences,
      exportedAt: DateTime.now().toIso8601String(),
    );

    return const JsonEncoder.withIndent('  ').convert(backup.toJson());
  }

  @override
  UserDataBackup? parseBackupFromJson(String jsonString) {
    try {
      final dynamic decoded = jsonDecode(jsonString);
      if (decoded is Map<String, dynamic>) {
        return UserDataBackup.fromJson(decoded);
      }
      return null;
    } catch (_) {
      return null;
    }
  }
}
