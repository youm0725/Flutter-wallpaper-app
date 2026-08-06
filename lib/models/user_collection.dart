import 'package:flutter/foundation.dart';

/// Immutable model representing a user-created custom wallpaper collection.
@immutable
final class UserCollection {
  final String id;
  final String name;
  final DateTime createdDate;
  final List<String> wallpaperIds;

  const UserCollection({
    required this.id,
    required this.name,
    required this.createdDate,
    required this.wallpaperIds,
  });

  /// Factory constructor to deserialize a [UserCollection] from a JSON map.
  factory UserCollection.fromJson(Map<String, dynamic> json) {
    return UserCollection(
      id: json['id'] as String? ?? '',
      name: json['name'] as String? ?? '',
      createdDate: json['createdDate'] != null
          ? DateTime.tryParse(json['createdDate'] as String) ?? DateTime.now()
          : DateTime.now(),
      wallpaperIds: (json['wallpaperIds'] as List<dynamic>?)
              ?.map((dynamic id) => id.toString())
              .toList() ??
          const <String>[],
    );
  }

  /// Serializes this [UserCollection] into a JSON map.
  Map<String, dynamic> toJson() {
    return <String, dynamic>{
      'id': id,
      'name': name,
      'createdDate': createdDate.toIso8601String(),
      'wallpaperIds': wallpaperIds,
    };
  }

  /// Returns a copy of this collection with updated properties.
  UserCollection copyWith({
    String? id,
    String? name,
    DateTime? createdDate,
    List<String>? wallpaperIds,
  }) {
    return UserCollection(
      id: id ?? this.id,
      name: name ?? this.name,
      createdDate: createdDate ?? this.createdDate,
      wallpaperIds: wallpaperIds ?? this.wallpaperIds,
    );
  }

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    return other is UserCollection &&
        other.id == id &&
        other.name == name &&
        other.createdDate == createdDate &&
        listEquals(other.wallpaperIds, wallpaperIds);
  }

  @override
  int get hashCode {
    return Object.hash(
      id,
      name,
      createdDate,
      Object.hashAll(wallpaperIds),
    );
  }
}
