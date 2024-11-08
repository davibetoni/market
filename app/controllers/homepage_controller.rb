# frozen_string_literal: true

# HomepageController
class HomepageController < ApplicationController
  def index
    @errors = params[:errors]
  end

  def info
    if must_return
      redirect_to root_path(errors: 'Preencha todos os campos')
      return
    end

    system("python3 app/jobs/esi/esi.py '#{info_params}'")

    sleep(2)

    # import json
    # params = json.loads(sys.argv[1])

    # type = params['tipo']
    # places = params['locais']
    # competition = params['concorrencia']
    # stores = params['comercios']
    # busy_streets = params['vias_movimentadas']
  end

  private

  def must_return
    params['tipo'].nil? || params['rendimento'].nil? || params['concorrencia'].nil? ||
      params['comercios'].nil? || params['vias_movimentadas'].nil?
  end

  def info_params
    params['rendimento'] = params['rendimento'].reject(&:empty?)
    params.except(:authenticity_token, :commit, :controller, :action).to_json
  end
end
