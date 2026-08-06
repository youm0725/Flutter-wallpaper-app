import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';
import '../models/user_preferences.dart';

/// Repository interface for managing user preferences.
abstract interface class IPreferencesRepository {
  Future<UserPreferences> getPreferences();
  Future<void> savePreferences(UserPreferences preferences);
  Future<void> resetPreferences();
}

/// Production implementation of [IPreferencesRepository] using [SharedPreferences].
final class LocalPreferencesRepository implements IPreferencesRepository {
  static const String _key = 'user_preferences_key';

  const LocalPreferencesRepository();

  @override
  Future<UserPreferences> getPreferences() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final jsonStr = prefs.getString(_key);
      if (jsonStr == null || jsonStr.isEmpty) {
        return const UserPreferences();
      }

      final Map<String, dynamic> map =
          jsonDecode(jsonStr) as Map<String, dynamic>;
      return UserPreferences.fromJson(map);
    } catch (_) {
      return const UserPreferences();
    }
  }

  @override
  Future<void> savePreferences(UserPreferences preferences) async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final jsonStr = jsonEncode(preferences.toJson());
      await prefs.setString(_key, jsonStr);
    } catch (_) {}
  }

  @override
  Future<void> resetPreferences() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.remove(_key);
    } catch (_) {}
  }
}
