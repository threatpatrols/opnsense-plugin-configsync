<?php

/*
    Copyright (c) 2022 Threat Patrols Pty Ltd <contact@threatpatrols.com>
    Copyright (c) 2018 Verb Networks Pty Ltd <contact@verbnetworks.com>
    Copyright (c) 2018 Nicholas de Jong <me@nicholasdejong.com>
    All rights reserved.

    Redistribution and use in source and binary forms, with or without modification,
    are permitted provided that the following conditions are met:

    1. Redistributions of source code must retain the above copyright notice, this
       list of conditions and the following disclaimer.

    2. Redistributions in binary form must reproduce the above copyright notice,
       this list of conditions and the following disclaimer in the documentation
       and/or other materials provided with the distribution.

    THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
    ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
    WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
    DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR
    ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
    (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
    LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
    ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
    (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
    SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
*/

namespace ThreatPatrols\ConfigSync\Api;

use OPNsense\Base\ApiControllerBase;
use OPNsense\Core\Backend;

class FilesController extends ApiControllerBase
{
    public function listAction()
    {
        $response = array('status' => 'fail', 'message' => 'Invalid request');

        if ($this->request->isPost()) {
            $current_page = 1;
            if ($this->request->hasPost('current')) {
                $current_page = (int)$this->request->getPost('current');
            }

            $row_count = -1;
            if ($this->request->hasPost('rowCount')) {
                $row_count = (int)$this->request->getPost('rowCount');
            }

            $filter = '';
            if ($this->request->hasPost('searchPhrase')) {
                $filter = (string)$this->request->getPost('searchPhrase');
            }

            $sort_field = 'timestamp_synced';
            $sort_direction = SORT_DESC;
            if ($this->request->hasPost('sort') && is_array($this->request->getPost('sort'))) {
                $sort_field = array_keys($this->request->getPost('sort'))[0];
                if ($this->request->getPost("sort")[$sort_field] == 'asc') {
                    $sort_direction = SORT_ASC;
                }
            }

            $backend = new Backend();
            $configd_run = sprintf(
                'configsync list_synced_system_configs --filter=%s',
                escapeshellarg($filter)
            );
            $backend_response = json_decode(trim($backend->configdRun($configd_run)), true);

            if ($backend_response['status'] !== 'success') {
                return $response;
            }

            $response_dataset = array(
                'current' => $current_page,
                'rowCount' => 0,
                'rows' => array(),
                'total' => count($backend_response['data']),
            );

            $response_dataset_rows = array();
            foreach ($backend_response['data'] as $row_index => $properties) {
                try {
                    $timestamp_unixtime = intval(
                        substr($properties['Key'], (strpos($properties['Key'], 'config-') + 7), -4)
                    );
                    if (strpos($properties['Key'], 'config-current.xml')) {
                        $timestamp_created = "Latest";
                    } elseif ($timestamp_unixtime === 0) {
                        $timestamp_created = "Unknown";
                    } else {
                        $timestamp_created = gmdate("Y-m-d\TH:i:s\Z", $timestamp_unixtime);
                    }
                } catch (\Exception $e) {
                    $timestamp_created = "Unknown";
                }

                array_push($response_dataset_rows, array(
                    'timestamp_created' => $timestamp_created,
                    'timestamp_synced' => $properties['LastModified'],
                    'path' => $properties['Key'],
                    'storage_size' => array_key_exists('Size', $properties) ? $properties["Size"] : "Unknown",
                    'storage_class' => array_key_exists('StorageClass', $properties) ? $properties["StorageClass"] : "Unknown",
                    'storage_etag' => array_key_exists('ETag', $properties) ? $properties["ETag"] : "Unknown",
                ));
            }

            $response_dataset['rowCount'] = count($response_dataset['rows']);

            $index_first = ($current_page - 1) * $row_count;
            if ($row_count >= 0) {
                $index_last = ($current_page * $row_count) - 1;
            } else {
                $index_last = count($backend_response['data']) - 1;
            }
            foreach ($this->arraySortByColumn($response_dataset_rows, $sort_field, $sort_direction) as $row_index => $properties) {
                if ($row_index >= $index_first && $row_index <= $index_last) {
                    array_push($response_dataset['rows'], $properties);
                }
            }
            return $response_dataset;
        }
        return $response;
    }

    private function arraySortByColumn($array_data, $sort_column, $direction = SORT_ASC)
    {
        // https://stackoverflow.com/questions/2699086/how-to-sort-a-multi-dimensional-array-by-value
        $keys = array_column($array_data, $sort_column);
        array_multisort($keys, $direction, $array_data);
        return $array_data;
    }
}
