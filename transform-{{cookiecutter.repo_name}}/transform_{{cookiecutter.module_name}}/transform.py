"""
Module to handle pipeline for timeseries
"""
from datetime import datetime

import apache_beam as beam
import apache_beam.transforms.core as beam_core
from apache_beam.options.pipeline_options import PipelineOptions

from osiris.core.enums import TimeResolution
from osiris.pipelines.azure_data_storage import DataSets
from osiris.pipelines.file_io_connector import DatalakeFileSource


class Transform{{cookiecutter.class_name}:
    """
    TODO: add appropriate docstring
    """

    # pylint: disable=too-many-arguments, too-many-instance-attributes, too-few-public-methods
    def __init__(self, storage_account_url: str, filesystem_name: str, tenant_id: str, client_id: str,
                 client_secret: str, source_dataset_guid: str, destination_dataset_guid: str,
                 time_resolution: TimeResolution, max_files: int):
        """
        :param storage_account_url: The URL to Azure storage account.
        :param filesystem_name: The name of the filesystem.
        :param tenant_id: The tenant ID representing the organisation.
        :param client_id: The client ID (a string representing a GUID).
        :param client_secret: The client secret string.
        :param source_dataset_guid: The GUID for the source dataset.
        :param destination_dataset_guid: The GUID for the destination dataset.
        :param time_resolution: The time resolution to store the data in the destination dataset with.
        :param max_files: Number of files to process in every pipeline run.
        """
        if None in [storage_account_url, filesystem_name, tenant_id, client_id, client_secret, source_dataset_guid,
                    destination_dataset_guid, time_resolution, max_files]:
            raise TypeError

        self.storage_account_url = storage_account_url
        self.filesystem_name = filesystem_name
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.client_secret = client_secret
        self.source_dataset_guid = source_dataset_guid
        self.destination_dataset_guid = destination_dataset_guid
        self.time_resolution = time_resolution
        self.max_files = max_files

    def transform(self, ingest_time: datetime = None):
        """
        TODO: add appropriate docstring
        """

        datasets = DataSets(tenant_id=self.tenant_id,
                            client_id=self.client_id,
                            client_secret=self.client_secret,
                            account_url=self.storage_account_url,
                            filesystem_name=self.filesystem_name,
                            source=self.source_dataset_guid,
                            destination=self.destination_dataset_guid,
                            time_resolution=self.time_resolution)

        while True:

            datalake_connector = DatalakeFileSource(tenant_id=self.tenant_id,
                                                    client_id=self.client_id,
                                                    client_secret=self.client_secret,
                                                    account_url=self.storage_account_url,
                                                    filesystem_name=self.filesystem_name,
                                                    guid=self.source_dataset_guid,
                                                    ingest_time=ingest_time,
                                                    max_files=self.max_files)

            if datalake_connector.estimate_size() == 0:
                break

            with beam.Pipeline(options=PipelineOptions(['--runner=DirectRunner'])) as pipeline:
                _ = (
                        pipeline  # noqa
                        | 'read from filesystem' >> beam.io.Read(datalake_connector)  # noqa

                        # TODO: Implement rest of the pipeline
                )

            datalake_connector.close()

            if ingest_time:
                break
