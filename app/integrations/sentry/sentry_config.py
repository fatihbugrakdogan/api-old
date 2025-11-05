import sentry_sdk
import os

class SentryConfig:
    def __init__(self):
        self.sentry_sdk = sentry_sdk

    def init(self):
        self.sentry_sdk.init(
            dsn=os.getenv("SENTRY_DSN"),
            _experiments={"enable_logs": True},
            traces_sample_rate=1.0,
            enable_tracing=True,
            
        )

    def send_error_to_sentry(self, error_mesage,details):
        self.sentry_sdk.logger.error(error_mesage, attributes=details)
        sentry_sdk.capture_message(error_mesage, level="error", extras=details)

    def send_info_to_sentry(self, info_mesage,details):
        self.sentry_sdk.logger.info(info_mesage, attributes=details)
        sentry_sdk.add_breadcrumb(message=info_mesage, level="info", category="info", data=details or {})

    def send_warning_to_sentry(self, warning_mesage,details):
        self.sentry_sdk.logger.warning(warning_mesage, attributes=details)

    def send_debug_to_sentry(self, debug_mesage,details):
        self.sentry_sdk.logger.debug(debug_mesage, attributes=details)

    def send_fatal_to_sentry(self, fatal_mesage,details):
        self.sentry_sdk.logger.fatal(fatal_mesage, attributes=details)


sentry_config = SentryConfig()
sentry_config.init()

