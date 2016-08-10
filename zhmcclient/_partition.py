# Copyright 2016 IBM Corp. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
A **partition** is a subset of a physical z Systems or LinuxONE computer
that is in DPM mode (Dynamic Partition Manager mode).
Objects of this class are not provided when the CPC is not in DPM mode.

A partition is always contained in a CPC.

Partitions can be created and deleted dynamically, and their resources such
as CPU, memory or I/O devices can be configured dynamically.
You can create as many partition definitions as you want, but only a specific
number of partitions can be active at any given time.

TODO: How can a user find out what the maximum is, before it is reached?
"""

from __future__ import absolute_import

from ._manager import BaseManager
from ._resource import BaseResource

__all__ = ['PartitionManager', 'Partition']


class PartitionManager(BaseManager):
    """
    Manager object for Partitions. This manager object is scoped to the
    partitions of a particular CPC.

    Derived from :class:`~zhmcclient.BaseManager`; see there for common methods
    and attributes.
    """

    def __init__(self, cpc):
        """
        Parameters:

          cpc (:class:`~zhmcclient.Cpc`):
            CPC defining the scope for this manager object.
        """
        super(PartitionManager, self).__init__(cpc)

    @property
    def cpc(self):
        """
        :class:`~zhmcclient.Cpc`: Parent object (CPC) defining the scope for
        this manager object.
        """
        return self._parent

    def list(self, full_properties=False):
        """
        List the partitions in scope of this manager object.

        Parameters:

          full_properties (bool):
            Controls whether the full set of resource properties should be
            retrieved, vs. only the short set as returned by the list
            operation.

        Returns:

          : A list of :class:`~zhmcclient.Partition` objects.

        Raises:

          :exc:`~zhmcclient.HTTPError`
          :exc:`~zhmcclient.ParseError`
          :exc:`~zhmcclient.AuthError`
          :exc:`~zhmcclient.ConnectionError`
        """
        cpc_uri = self.cpc.get_property('object-uri')
        partitions_res = self.session.get(cpc_uri + '/partitions')
        partition_list = []
        if partitions_res:
            partition_items = partitions_res['partitions']
            for partition_props in partition_items:
                partition = Partition(self, partition_props)
                if full_properties:
                    partition.pull_full_properties()
                partition_list.append(partition)
        return partition_list

    def create(self, properties):
        """
        Create a partition with the specified resource properties.

        Parameters:

          properties (dict): Properties for the new partition.

        Returns:

          string: The resource URI of the new partition.

        Raises:

          :exc:`~zhmcclient.HTTPError`
          :exc:`~zhmcclient.ParseError`
          :exc:`~zhmcclient.AuthError`
          :exc:`~zhmcclient.ConnectionError`
        """
        cpc_uri = self.cpc.get_property('object-uri')
        result = self.session.post(cpc_uri + '/partitions', body=properties)
        return result['object-uri']


class Partition(BaseResource):
    """
    Representation of a Partition.

    Derived from :class:`~zhmcclient.BaseResource`; see there for common
    methods and attributes.
    """

    def __init__(self, manager, properties):
        """
        Parameters:

          manager (:class:`~zhmcclient.PartitionManager`):
            Manager object for this resource.

          properties (dict):
            Properties to be set for this resource object.
            See initialization of :class:`~zhmcclient.BaseResource` for
            details.
        """
        assert isinstance(manager, PartitionManager)
        super(Partition, self).__init__(manager, properties)

    def start(self, wait_for_completion=True):
        """
        Start (activate) this partition.

        TODO: Describe what happens if the maximum number of active partitions
        is exceeded.

        Parameters:

          wait_for_completion (bool):
            Boolean indicating whether the method should wait until
            the operation/job has completed.
            If wait_for_completion is 'False' the status of the operation/job
            has to be retrieved via the method 'query_job_status' method.

        Returns:

          :term:`json object` with the operation result.

            In the default case of a synchronous operation
            (wait_for_completion=True) the return value is a JSON object with
            members like status, job-status-code and job-reason-code.
            See the respective sections in :term:`HMC API` for a description
            of the response body contents of the Query Job Status operation.

            In case of an asynchronous operation (wait_for_completion=False),
            the return value is a JSON object with a member job-id whose value
            needs to be used for query_job_status().

        Raises:

          :exc:`~zhmcclient.HTTPError`
          :exc:`~zhmcclient.ParseError`
          :exc:`~zhmcclient.AuthError`
          :exc:`~zhmcclient.ConnectionError`
        """
        partition_uri = self.get_property('object-uri')
        result = self.manager.session.post(partition_uri + '/operations/start',
            wait_for_completion=wait_for_completion)
        return result

    def stop(self, wait_for_completion=True):
        """
        Stop (deactivate) this partition.

        Parameters:

          wait_for_completion (bool):
            Boolean indicating whether the method should wait until
            the operation/job has completed.
            If wait_for_completion is 'False' the status of the operation/job
            has to be retrieved via the method 'query_job_status' method.

        Returns:

          :term:`json object` with the operation result.

            In the default case of a synchronous operation
            (wait_for_completion=True) the return value is a JSON object with
            members like status, job-status-code and job-reason-code.
            See the respective sections in :term:`HMC API` for a description
            of the response body contents of the Query Job Status operation.

            In case of an asynchronous operation (wait_for_completion=False),
            the return value is a JSON object with a member job-id whose value
            needs to be used for query_job_status().

        Raises:

          :exc:`~zhmcclient.HTTPError`
          :exc:`~zhmcclient.ParseError`
          :exc:`~zhmcclient.AuthError`
          :exc:`~zhmcclient.ConnectionError`
        """
        partition_uri = self.get_property('object-uri')
        result = self.manager.session.post(partition_uri + '/operations/stop',
            wait_for_completion=wait_for_completion)
        return result

    def delete(self):
        """
        Deletes this partition.

        Raises:

          :exc:`~zhmcclient.HTTPError`
          :exc:`~zhmcclient.ParseError`
          :exc:`~zhmcclient.AuthError`
          :exc:`~zhmcclient.ConnectionError`
        """
        partition_uri = self.get_property('object-uri')
        self.manager.session.delete(partition_uri)

    def update_properties(self, properties):
        """
        Updates one or more of the writable properties of a partition
        with the specified resource properties.

        Parameters:

          properties (dict): Updated properties for the partition.

        Raises:

          :exc:`~zhmcclient.HTTPError`
          :exc:`~zhmcclient.ParseError`
          :exc:`~zhmcclient.AuthError`
          :exc:`~zhmcclient.ConnectionError`
        """
        partition_uri = self.get_property('object-uri')
        self.manager.session.post(partition_uri, body=properties)

