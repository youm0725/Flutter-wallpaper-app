import 'package:flutter/material.dart';

/// Favorites Screen placeholder.
class FavoritesScreen extends StatelessWidget {
  const FavoritesScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Favorites'),
      ),
      body: const Center(
        child: Text(
          'Favorites Feature Coming Soon',
          style: TextStyle(fontSize: 16.0),
        ),
      ),
    );
  }
}
