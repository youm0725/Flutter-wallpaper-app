import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../core/constants/app_info.dart';
import '../../core/constants/app_sizes.dart';
import '../../core/router/route_constants.dart';
import '../../providers/app_info_provider.dart';
import '../../providers/engagement_provider.dart';

/// About screen — app identity, version, links to legal pages, and support.
class AboutScreen extends ConsumerWidget {
  const AboutScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final asyncInfo = ref.watch(packageInfoProvider);
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(title: const Text('About')),
      body: SafeArea(
        child: ListView(
          physics: const BouncingScrollPhysics(),
          padding: const EdgeInsets.symmetric(vertical: AppSizes.p24),
          children: [
            // ── App Identity Header ─────────────────────────────────────
            _AboutHeader(asyncInfo: asyncInfo),

            const SizedBox(height: AppSizes.p32),

            // ── Legal Section ───────────────────────────────────────────
            _SectionLabel(title: 'Legal'),
            _InfoTile(
              icon: Icons.privacy_tip_outlined,
              title: 'Privacy Policy',
              subtitle: 'How we handle your data',
              onTap: () => context.pushNamed(RouteConstants.privacyName),
            ),
            _InfoTile(
              icon: Icons.gavel_outlined,
              title: 'Terms & Conditions',
              subtitle: 'Usage terms and content license',
              onTap: () => context.pushNamed(RouteConstants.termsName),
            ),
            _InfoTile(
              icon: Icons.code_rounded,
              title: 'Open Source Licenses',
              subtitle: 'Third-party Flutter packages',
              onTap: () => _showLicenses(context),
            ),

            const Divider(height: AppSizes.p32),

            // ── Support Section ─────────────────────────────────────────
            _SectionLabel(title: 'Support'),
            _InfoTile(
              icon: Icons.mail_outline_rounded,
              title: 'Contact Support',
              subtitle: AppInfo.supportEmail,
              onTap: () => _sendFeedback(context, ref),
            ),
            _InfoTile(
              icon: Icons.rate_review_outlined,
              title: 'Send Feedback',
              subtitle: 'Help us improve the app',
              onTap: () => _sendFeedback(context, ref),
            ),
            _InfoTile(
              icon: Icons.star_rate_rounded,
              title: 'Rate the App',
              subtitle: 'Share your experience on the store',
              onTap: () => requestAppReview(ref),
            ),

            const Divider(height: AppSizes.p32),

            // ── App Details ─────────────────────────────────────────────
            _SectionLabel(title: 'App Details'),
            asyncInfo.when(
              data: (info) => Column(
                children: [
                  _DetailRow(label: 'Version', value: info.version),
                  _DetailRow(label: 'Build', value: info.buildNumber),
                  _DetailRow(label: 'Package', value: info.packageName),
                ],
              ),
              loading: () => const Padding(
                padding: EdgeInsets.all(AppSizes.p16),
                child: Center(child: CircularProgressIndicator()),
              ),
              error: (_, _) => const SizedBox.shrink(),
            ),

            const SizedBox(height: AppSizes.p48),

            // ── Footer ──────────────────────────────────────────────────
            Center(
              child: Text(
                '© 2025 ${AppInfo.appName}',
                style: theme.textTheme.bodySmall?.copyWith(
                  color: theme.colorScheme.onSurfaceVariant,
                ),
              ),
            ),
            const SizedBox(height: AppSizes.p8),
            Center(
              child: Text(
                'Made with ❤️ for wallpaper enthusiasts',
                style: theme.textTheme.bodySmall?.copyWith(
                  color: theme.colorScheme.onSurfaceVariant,
                ),
              ),
            ),
            const SizedBox(height: AppSizes.p32),
          ],
        ),
      ),
    );
  }

  void _showLicenses(BuildContext context) {
    showLicensePage(
      context: context,
      applicationName: AppInfo.appName,
      applicationLegalese: '© 2025 ${AppInfo.appName}',
    );
  }

  Future<void> _sendFeedback(BuildContext context, WidgetRef ref) async {
    final success = await openFeedback(ref);
    if (!success && context.mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: const Text('No email app found. Please use support@wallpapergallery.app'),
          behavior: SnackBarBehavior.floating,
          margin: const EdgeInsets.all(AppSizes.p16),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(AppSizes.radiusSm),
          ),
        ),
      );
    }
  }
}


// ── Private Widgets ─────────────────────────────────────────────────────────

class _AboutHeader extends StatelessWidget {
  final AsyncValue<dynamic> asyncInfo;
  const _AboutHeader({required this.asyncInfo});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final versionStr = asyncInfo.value?.version as String? ?? '—';

    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: AppSizes.p24),
      child: Column(
        children: [
          // App icon placeholder
          Container(
            width: 96,
            height: 96,
            decoration: BoxDecoration(
              gradient: LinearGradient(
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
                colors: [
                  theme.colorScheme.primary,
                  theme.colorScheme.tertiary,
                ],
              ),
              borderRadius: BorderRadius.circular(AppSizes.radiusLg + 4),
              boxShadow: [
                BoxShadow(
                  color: theme.colorScheme.primary.withValues(alpha: 0.3),
                  blurRadius: 24,
                  offset: const Offset(0, 8),
                ),
              ],
            ),
            child: Icon(
              Icons.wallpaper_rounded,
              size: 48,
              color: theme.colorScheme.onPrimary,
            ),
          ),

          const SizedBox(height: AppSizes.p16),

          Text(
            AppInfo.appName,
            style: theme.textTheme.headlineSmall?.copyWith(
              fontWeight: FontWeight.w800,
              letterSpacing: -0.5,
            ),
          ),

          const SizedBox(height: AppSizes.p4),

          Text(
            'Version $versionStr',
            style: theme.textTheme.labelMedium?.copyWith(
              color: theme.colorScheme.primary,
              fontWeight: FontWeight.w600,
            ),
          ),

          const SizedBox(height: AppSizes.p12),

          Text(
            AppInfo.description,
            textAlign: TextAlign.center,
            style: theme.textTheme.bodyMedium?.copyWith(
              color: theme.colorScheme.onSurfaceVariant,
              height: 1.5,
            ),
          ),

          const SizedBox(height: AppSizes.p16),

          // Key feature badges
          Wrap(
            spacing: AppSizes.p8,
            runSpacing: AppSizes.p8,
            alignment: WrapAlignment.center,
            children: const [
              _FeatureBadge(icon: Icons.wifi_off_rounded, label: 'Offline'),
              _FeatureBadge(icon: Icons.no_accounts_outlined, label: 'No Account'),
              _FeatureBadge(icon: Icons.security_outlined, label: 'Private'),
            ],
          ),
        ],
      ),
    );
  }
}

class _FeatureBadge extends StatelessWidget {
  final IconData icon;
  final String label;
  const _FeatureBadge({required this.icon, required this.label});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Container(
      padding: const EdgeInsets.symmetric(
        horizontal: AppSizes.p12,
        vertical: AppSizes.p6,
      ),
      decoration: BoxDecoration(
        color: theme.colorScheme.primaryContainer.withValues(alpha: 0.6),
        borderRadius: BorderRadius.circular(AppSizes.radiusSm),
        border: Border.all(
          color: theme.colorScheme.primary.withValues(alpha: 0.2),
        ),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 12, color: theme.colorScheme.primary),
          const SizedBox(width: AppSizes.p4),
          Text(
            label,
            style: theme.textTheme.labelSmall?.copyWith(
              color: theme.colorScheme.primary,
              fontWeight: FontWeight.w600,
            ),
          ),
        ],
      ),
    );
  }
}

class _SectionLabel extends StatelessWidget {
  final String title;
  const _SectionLabel({required this.title});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Padding(
      padding: const EdgeInsets.fromLTRB(
          AppSizes.p16, AppSizes.p8, AppSizes.p16, AppSizes.p4),
      child: Text(
        title,
        style: theme.textTheme.labelMedium?.copyWith(
          fontWeight: FontWeight.w700,
          color: theme.colorScheme.primary,
          letterSpacing: 0.5,
        ),
      ),
    );
  }
}

class _InfoTile extends StatelessWidget {
  final IconData icon;
  final String title;
  final String subtitle;
  final VoidCallback? onTap;

  const _InfoTile({
    required this.icon,
    required this.title,
    required this.subtitle,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return ListTile(
      onTap: onTap,
      leading: CircleAvatar(
        radius: 18,
        backgroundColor: theme.colorScheme.surfaceContainerHighest,
        child: Icon(icon, size: 18, color: theme.colorScheme.primary),
      ),
      title: Text(
        title,
        style: theme.textTheme.bodyMedium?.copyWith(
          fontWeight: FontWeight.w600,
        ),
      ),
      subtitle: Text(
        subtitle,
        style: theme.textTheme.bodySmall?.copyWith(
          color: theme.colorScheme.onSurfaceVariant,
        ),
      ),
      trailing: onTap != null
          ? Icon(Icons.chevron_right_rounded,
              color: theme.colorScheme.onSurfaceVariant)
          : null,
    );
  }
}

class _DetailRow extends StatelessWidget {
  final String label;
  final String value;
  const _DetailRow({required this.label, required this.value});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Padding(
      padding: const EdgeInsets.symmetric(
          horizontal: AppSizes.p16, vertical: AppSizes.p8),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(
            label,
            style: theme.textTheme.bodyMedium?.copyWith(
              color: theme.colorScheme.onSurfaceVariant,
            ),
          ),
          Text(
            value,
            style: theme.textTheme.bodyMedium?.copyWith(
              fontWeight: FontWeight.w600,
            ),
          ),
        ],
      ),
    );
  }
}
