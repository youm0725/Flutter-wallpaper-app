import 'package:flutter/foundation.dart';

/// Immutable model representing a curated wallpaper collection.
@immutable
final class Collection {
  final String id;
  final String title;
  final String description;
  final String coverImagePath;
  final List<String> wallpaperIds;

  const Collection({
    required this.id,
    required this.title,
    required this.description,
    required this.coverImagePath,
    required this.wallpaperIds,
  });

  /// Factory constructor to create a [Collection] from a JSON map.
  factory Collection.fromJson(Map<String, dynamic> json) {
    return Collection(
      id: json['id'] as String? ?? '',
      title: json['title'] as String? ?? '',
      description: json['description'] as String? ?? '',
      coverImagePath: json['coverImagePath'] as String? ?? '',
      wallpaperIds: (json['wallpaperIds'] as List<dynamic>?)
              ?.map((dynamic id) => id.toString())
              .toList() ??
          const <String>[],
    );
  }

  /// Converts this [Collection] instance to a JSON map.
  Map<String, dynamic> toJson() {
    return <String, dynamic>{
      'id': id,
      'title': title,
      'description': description,
      'coverImagePath': coverImagePath,
      'wallpaperIds': wallpaperIds,
    };
  }

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    return other is Collection &&
        other.id == id &&
        other.title == title &&
        other.description == description &&
        other.coverImagePath == coverImagePath &&
        listEquals(other.wallpaperIds, wallpaperIds);
  }

  @override
  int get hashCode {
    return Object.hash(
      id,
      title,
      description,
      coverImagePath,
      Object.hashAll(wallpaperIds),
    );
  }
}
