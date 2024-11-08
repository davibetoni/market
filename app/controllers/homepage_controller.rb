# frozen_string_literal: true

# HomepageController
class HomepageController < ApplicationController
  before_action :set_variables, only: %i[index]

  def index
    @errors = params[:errors]
  end

  def info
    params['income'] = params['income'].reject(&:empty?)

    if must_return
      redirect_to root_path(errors: 'Preencha todos os campos')
      return
    end

    system("python3 app/jobs/esi/esi.py '#{info_params}'")

    sleep(2)
  end

  private

  def set_variables
    # Mais de 2 a 3 SM:
    @initial_group = %w[
      350600305000103 350600305000191 350600305000194 350600305000197 350600305000301
      350600305000449 350600305000505
    ]

    # Mais de 3 a 5 SM:
    @second_group = %w[
      350600305000102 350600305000106 350600305000108 350600305000025 350600305000059 350600305000061 350600305000099
      350600305000144 350600305000148 350600305000149 350600305000153 350600305000193 350600305000250 350600305000252
      350600305000259 350600305000260 350600305000261 350600305000299 350600305000300 350600305000343 350600305000381
      350600305000481 350600305000482 350600305000490 350600305000497
    ]
    # Mais de 5 a 10 SM:
    @third_group = %w[
      350600305000104 350600305000105 350600305000107 350600305000537 350600305000538 350600305000151 350600305000154
      350600305000155 350600305000156 350600305000157 350600305000195 350600305000196 350600305000198 350600305000199
      350600305000200 350600305000201 350600305000202 350600305000203 350600305000204 350600305000256 350600305000257
      350600305000258 350600305000297 350600305000298 350600305000344 350600305000377 350600305000410 350600305000411
      350600305000480 350600305000487 350600305000506 350600305000509
    ]

    # Mais de 10 SM:
    @fourth_group = %w[
      350600305000450
    ]
  end

  def must_return
    params.values_at('type', 'income', 'trading', 'another_markets', 'busy_streets').any?(&:blank?)
  end

  def info_params
    params.except(:authenticity_token, :commit, :controller, :action).to_json
  end
end
